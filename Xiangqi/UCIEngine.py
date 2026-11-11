import os
import subprocess
import threading
import queue
import re
from urllib.parse import urlparse
import requests
from Xiangqi import *


class UCIEngine:
    def __init__(self, backend='fairyxq'):

        self.engine_download(backend)
        
        self.proc = subprocess.Popen(
            [os.path.join(os.getcwd(), backend)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        self.q = queue.Queue()
        
        self.reader = threading.Thread(target=self.reader, daemon=True)
        self.reader.start()
        
        print("Engine starts up ...... ready!")

        # Initialize UCI  
        self.write("uci")  # tell engine to enter UCI mode
        self.read_until("uciok")

        # Make sure engine is ready
        self.write("isready")
        self.read_until("readyok")
        
        # Set Xiangqi variant if needed
        self.write("setoption name UCI_Variant value xiangqi")
        self.write("isready")
        self.read_until("readyok")

        if backend.lower=='fairystockfishnnue':
            self.write(f"setoption name EvalFile value {NNUE_PATH}")
            self.write(f"setoption name Use NNUE value true")
        elif backend.lower=="fairyxq":
            self.write(f"setoption name Use NNUE value false")
        elif backend.lower=="pikafish":
            self.write(f"setoption name Use NNUE value true")

        self.write("isready")
        self.read_until("readyok")

    def engine_download(self, backend="fairyxq"): 
        # download engine and nnue weights
        if not os.path.exists(backend):
            if backend.lower()=='fairyxq':
                url = ["https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/fairyxq"]
                #url = ["https://github.com/fairy-stockfish/Fairy-Stockfish/releases/latest/download/fairy-stockfish-largeboard_x86-64"]
            elif backend.lower()=='stockfishnnue':
                url=[]
            elif backend.lower()=='pikafish':
                print("Pikafish requires NNUE net file!")
                url = ["https://github.com/official-pikafish/Networks/releases/download/master-net/pikafish.nnue",
                    "https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/pikafish"]

            for each in url:
                r = requests.get(each,stream=True)
                r.raise_for_status()
                file_name= os.path.basename(urlparse(each).path)
                with open(file_name, "wb") as f:
                    f.write(r.content)
                print(f"{file_name} downloading ...... done!")

        # Make it executable
        file_name = os.path.basename(backend)
        os.system(f"chmod +x {file_name}")

        if os.access(backend, os.X_OK):
            print(f"{file_name} engine downloading ...... done!")
    
    def is_alive(self):
        return self.proc.poll() is None

    def close(self):
        # Quit engine
        self.write("quit")
        self.proc.terminate()
        
    def write(self, cmd):
        if isinstance(cmd, bytes):
            data = cmd.decode()
        else:
            data = (cmd + "\n")
        self.proc.stdin.write(data)
        self.proc.stdin.flush()
    
        
    def reader(self):
        try:
            for line in self.proc.stdout:
                if isinstance(line, bytes):
                    line = line.decode()
                line = line.strip()
                self.q.put(line)
        finally:
            self.q.put(None)

    def read_line(self, timeout=1.0):
        try:
            return self.q.get(timeout=timeout)
        except queue.Empty:
            return None
        
    def read_until(self, keyword, timeout=1.0):  
        lines = []  
        while True:  
            try:  
                line = self.q.get(timeout=timeout)  
            except queue.Empty:  
                break  
            if isinstance(line, bytes):  
                line = line.decode()  
            line = line.strip()  
            lines.append(line)  
            if keyword in line:  
                break  
        return lines

    def legal_moves(self, fen): 
        self.write("ucinewgame")
        self.write("isready")
        self.read_until("readyok")
        
        self.write(f"position fen {fen}")
        self.write("go perft 1")
        out = self.read_until("Nodes searched:")

        line = self.read_line()
        if line:
            out.append(line)
                
        moves = []
        for line in out:
            # Parse Legal moves:
            line = line.strip()
            if ":" in line and not any(x in line for x in ["Nodes", "info string"]):
                move = line.split(":")[0].strip()
                moves.append(move)
        
        return moves

    def onemove(self, fen):
    
        # Start new game
        self.write("ucinewgame")
        self.write("isready")
        self.read_until("readyok")

        # Load position
        self.write(f"position fen {fen}")

        # Ask engine to search
        self.write(f"go depth 1")
      
        """
        'info string classical evaluation enabled',
        'info depth 1 seldepth 1 multipv 1 score cp -669 nodes 99 nps 33000 tbhits 0 time 3 pv g3g10 d10d9',
        'bestmove g3g10 ponder d10d9'
        """
        
        out  = self.read_until("bestmove")

        results =[]
        
        for line in out:
            # Parse info
            if line.startswith("info"):
                m = re.search(r"info depth (\d+).*?score (cp|mate) (-?\d+).*?pv (.+)",line)
                if m:
                    depth=int(m.group(1))
                    score_type=m.group(2)
                    score=int(m.group(3))
                    pv=m.group(4).split()               

        return {"depth": depth, 
                "score_type": score_type, 
                "score":score, 
                "pv":pv}
        
    def bestmove(self, fen, depth=10,timeout=1.0):
        """
        Analyze a Xiangqi position given by a FEN string.
        Returns the engine's best move and principal variation (PV).

        :param fen: str, Xiangqiselfnt, search depth
        :return: tuple (bestmove, pv) where pv is a list of moves in UCI format
        """
        
        # Start new game
        self.write("ucinewgame")
        self.write("isready")
        self.read_until("readyok")

        # Load position
        self.write(f"position fen {fen}")

        # Ask engine to search
        self.write(f"go depth {depth}")

        bestmove = None
        ponder = None
        pv_moves = []

        out  = self.read_until("bestmove",timeout)

        for line in out:
            # Parse bestmove
            if line.startswith("bestmove"):
                parts = line.split()
                bestmove = parts[1]
                # Check if there is ponder move
                if len(parts) >= 4 and parts[2] == "ponder":
                    ponder=parts[3]

            # Parse PV from info lines
            if " pv " in line:
                # Example: info depth 10 score cp 34 pv f7e5 e3f5 d9e7 ...
                parts = line.split(" pv ")
                if len(parts) >= 2:
                    pv_moves = parts[1].split()

        return {
            "bestmove": bestmove, 
            "pv": pv_moves,
            "ponder": ponder
        }
        
    def multipv(self, fen, depth=1, multipv=20):
        """Return {bestmove, pv_list}."""

        # Start new game
        self.write("ucinewgame")
        self.write("isready")
        self.read_until("readyok")

        # Send multipv
        if multipv > 1:
            self.write(f"setoption name MultiPV value {multipv}")

        self.write("isready")
        self.read_until("readyok")
    
        self.write(f"position fen {fen}")
        self.write(f"go depth {depth}")

        out = self.read_until("bestmove")

        """
        info depth 27 seldepth 59 multipv 1 score cp 0 nodes 6509485 nps 476396 hashfull 999 tbhits 0 time 13664 pv g7f7 
        """

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

                idx = parts.index("depth")
                depth_idx = int(parts[idx + 1])
                
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
                root_move = parts[parts.index("pv") + 1]
                
                pv_moves = l.split(" pv ")[1].split()

                pv_list.append((depth_idx, pv_idx, score, pv_moves))

        # Sort PV lines by depth index
        pv_list.sort(key=lambda x: (x[0],x[1]))

        return {
            "out":out,
            "bestmove": bestmove,
            "pv": pv_list
        }
    
    def eval(self, fens):
        
        self.write("setoption name Use NNUE value true")
        
        score=[]
        for fen in fens:
            self.write("ucinewgame")
            self.write("isready")
            self.read_until("readyok")

            self.write(f"position fen '{fen}'")
            self.write("eval")
            output= self.read_until("Final")
            output = "\n".join(output)
        
            m = re.search(r"Final evaluation\s+([+-]?\d+\.?\d*)", output)
            score.append(float(m.group(1)) if m else None)

            buckets = {
                int(b): float(v.replace(' ', ''))
                for b, v in re.findall(
                r'\|\s*(\d+)\s*\|\s*([+-]\s*[\d.]+)',
                text
                )
            }

            used_bucket = int(re.search(
                r'<-- this bucket is used',
                text
            ) is not None)

            nnue = float(re.search(
                r'NNUE evaluation\s+([+-]\d+)',
                text
            ).group(1))

            white_nnue = float(re.search(
                r'NNUE evaluation\s+([+-]\s*[\d.]+)\s+\(white side\)',
                text
            ).group(1).replace(' ', ''))
        
        return score
