import subprocess
import threading
import queue

class UCIEngine:
    def __init__(self, path):
        self.proc = subprocess.Popen(
            [path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        self.q = queue.Queue()
        self.reader = threading.Thread(target=self._read_output, daemon=True)
        self.reader.start()

    def _read_output(self):
        for line in self.proc.stdout:
            self.q.put(line.strip())

    def write(self, cmd):
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def read_until(self, keyword):
        lines = []
        while True:
            try:
                line = self.q.get(timeout=1)
            except queue.Empty:
                break
            lines.append(line)
            if keyword in line:
                break
        return lines

    def analyze(self, fen, depth=10, multipv=1):
        """Return {bestmove, pv_list}."""

        # Init
        self.write("uci")
        self.read_until("uciok")

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
        self.write("quit")
        self.proc.terminate()
