import subprocess
import threading
import queue
import os
import requests
from Xiangqi import *

class UCIEngine:
    def __init__(self, ENGINE_PATH, NNUE_PATH):

        self.proc = subprocess.Popen(
            [ENGINE_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
           # universal_newlines=True,
            text=True,
            bufsize=1
        )
        self.q = queue.Queue()
        self.reader = threading.Thread(target=self.read, daemon=True)
        self.reader.start()
        print("Engine starts up ...... ready!")

        # Init
        self.write("uci")
        self.read_until("uciok")
        
        # Set Xiangqi variant if needed
        self.write("setoption name UCI_Variant value xiangqi")
        self.write("isready")
        self.read_until("readyok")

        self.write(f"setoption name EvalFile value {NNUE_PATH}")
        self.write("isready")
        self.read_until("readyok")

    def write(self, cmd):
        if isinstance(cmd, bytes):
            data = cmd.decode()
        else:
            data = (cmd + "\n")
        self.proc.stdin.write(data)
        self.proc.stdin.flush()
    
        
    def read(self):
        for line in self.proc.stdout:
            if isinstance(line, bytes):
                line = line.decode()
            line = line.strip()
            self.q.put(line)

    def read_until(self, keyword):
        lines = []
        while True:
            try:
                line = self.q.get(timeout=1)
            except queue.Empty:
                break
            if isinstance(line, bytes):
                line = line.decode()
            line = line.strip()
            lines.append(line)
            if keyword in line:
                break
        return lines

    def bestmove(self, fen, depth=10):
        """
        Analyze a Xiangqi position given by a FEN string.
        Returns the engine's best move and principal variation (PV).

        :param fen: str, Xiangqi FEN string
        :param depth: int, search depth
        :return: tuple (bestmove, pv) where pv is a list of moves in UCI format
        """
        
        # Start new game
        self.write("ucinewgame")

        # Load position
        self.write(f"position fen {fen}")

        # Ask engine to search
        self.write(f"go depth {depth}")

        bestmove = None
        pv_moves = []

        out  = self.read_until("bestmove")

        for line in out:
            # Parse bestmove
            if line.startswith("bestmove"):
                parts = line.split()
                bestmove = parts[1]
                # Check if there is ponder move
                if len(parts) >= 4 and parts[2] == "ponder":
                    pv_moves.append(parts[3])

            # Parse PV from info lines
            if " pv " in line:
                # Example: info depth 10 score cp 34 pv f7e5 e3f5 d9e7 ...
                parts = line.split(" pv ")
                if len(parts) >= 2:
                    pv_moves = parts[1].split()

        return {
            "bestmove": bestmove, 
            "pv": pv_moves
        }
        
    def multipv(self, fen, depth=10,multipv=1):
        """Return {bestmove, pv_list}."""

        # Init
        self.write("uci")
        self.read_until("uciok")

        # Start new game
        self.write("ucinewgame")

        # Set Xiangqi variant if needed
        self.write("setoption name UCI_Variant value xiangqi")
        
        # Send multipv
        if multipv > 1:
            self.write(f"setoption name MultiPV value {multipv}")

        self.write(f"position fen {fen}")
        self.write(f"go depth {depth}")

        out = self.read_until("bestmove")

        bestmove = None
        pv_list = []   # list of (multipv index, score, pv_moves)

        for l in out:
            # Parse bestmove
            if l.startswith("bestmove"):
                bestmove = l.split()[1]

            # Parse PV
            # Example:
            # info depth 12 multipv 1 score cp 38 pv h2e2 e3e7 …
            if " pv " in l and "multipv" in l:
                parts = l.split()
                idx = parts.index("multipv")
                pv_idx = int(parts[idx + 1])

                # score cp or mate
                if "score" in parts:
                    s_idx = parts.index("score")
                    score_type = parts[s_idx + 1]
                    score_val = parts[s_idx + 2]
                    if score_type == "cp":
                        score = int(score_val)
                    else:
                        score = f"mate {score_val}"
                else:
                    score = None

                # extract pv sequence after "pv"
                pv_moves = l.split(" pv ")[1].split()

                pv_list.append((pv_idx, score, pv_moves))

        # Sort PV lines by multipv index
        pv_list.sort(key=lambda x: x[0])

        return {
            "bestmove": bestmove,
            "pv": pv_list
        }

    def close(self):
        # Quit engine
        self.write("quit")
        self.proc.terminate()
    
    def _nnue_eval_fen(self, fen):
        # Set the position
        self.write(f"position fen {fen}")
        self.write("eval")
    
        # Read until we get a score
        lines = self.read_until("Final")
    
        # Look for a line containing NNUE score
        for line in lines:
            print(f"Debug: {line}")
            if "Final" in line and "evaluation" in line:
                # Example line: "Final evaluation: +23"
                parts = line.split(":")
                if len(parts)>=2:
                    score = parts[1].strip()
                    return score

        return None  # if nothing found

    def nnue(self, fens):
        
        score=[]
        for fen in fens:
            score.append(self._nnue_eval_fen(fen))

        return score

