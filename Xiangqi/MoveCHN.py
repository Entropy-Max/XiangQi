from collections import defaultdict
from Xiangqi.common import *
from Xiangqi.FEN import FEN
from Xiangqi.Move import Move
import re

class MoveCHN(Move):

    def __init__(self,fen,moves):
        super().__init__(fen,moves)
        self.moves=moves
        self.movesCHN=[]
        self.piece_counts = {}
        self.piece_moves = {} # piece move history dict      
        self.init_piece_moves()

    def init_piece_moves(self):
        """
        Create a mapping of all 32 pieces to their initial positions and move lists.
        """    

        for r, row in enumerate(self.board):
            for c, cell in enumerate(row):
                if cell == '.':
                    continue
                count = self.piece_counts.get(cell, 0) + 1
                self.piece_counts[cell] = count
                pid = f"{cell}{count}"  # e.g. R1, R2, N1, n2
                self.piece_moves[pid] = [(r, c)]
    

    def _parse_move(self, move, side='auto'):

        move = move.replace(' ', '')
        if len(move) != 4:
            raise ValueError(f"Move must have 4 chars like 炮二平五, got: {move}")

        # Normalize black numerals from full-width to ASCII

        fw_digits = '０１２３４５６７８９'
        ascii_digits = '0123456789'
        for fw, a in zip(fw_digits, ascii_digits):
            move = move.replace(fw, a)

        first, second, third, fourth = move

        # pattern detection
        if first in PIECES and second in NUMS:
            piece, hint, pattern = first, second, 'piece+file'
        elif first in HINTS and second in PIECES:
            hint, piece, pattern = first, second, 'hint+piece'
        else:
            raise ValueError(f"Invalid move structure: {move}")

        if third not in ACTIONS or fourth not in NUMS:
            raise ValueError(f"Invalid action/target in move: {move}")

        # auto-detect side if requested
        if side == 'auto':
            if second in chinese_nums or fourth in chinese_nums:
                side = 'red'
            else:
                side = 'black'

        mapped = piece_map_cte.get(piece)
        if not mapped:
            raise ValueError(f"Unknown piece: {piece}")
        mapped = mapped.upper() if side == 'red' else mapped.lower()

        # all positions for that piece
        positions = [(r, c) for r, row in enumerate(self.board) for c, cell in enumerate(row) if cell == mapped]
        if not positions:
            raise ValueError(f"No piece {piece} ({mapped}) found on board.")

        # find starting piece
        start = None
        if pattern == 'piece+file':
            file_num = numerals_cte(second)
            # mapping: from player's file-number to board column
            start_col = 9 - file_num if side == 'red' else file_num - 1
            same_col = [pos for pos in positions if pos[1] == start_col]
            if len(same_col) == 1:
                start = same_col[0]
            else:
                # ambiguous or not found
                return None
        else:  # hint + piece (前/中/后)
            col_groups = defaultdict(list)
            for r, c in positions:
                col_groups[c].append((r, c))
            multi_files = [c for c, grp in col_groups.items() if len(grp) >= 2]
            if len(multi_files) != 1:
                return None
            col = multi_files[0]
            grp = col_groups[col]
            # when sorting, the "前" piece is the one nearer the opponent.
            # since row 0 is black side, red moves up (toward row 0), black moves down.
            grp.sort(key=lambda x: x[0], reverse=(side == 'black'))
            if hint == '前':
                start = grp[0]
            elif hint == '中':
                start = grp[len(grp)//2]
            elif hint == '后':
                start = grp[-1]
            else:
                return None

        sr, sc = start

        # FIXED: red moves UP (row decreases), black moves DOWN (row increases)
        forward = -1 if side == 'red' else 1

        num = numerals_cte(fourth)
        piece_type = mapped.upper()
        tr, tc = sr, sc

        if third == '平':
            tc = 9 - num if side == 'red' else num - 1
        elif third in ('进', '退'):
            if piece_type in ('R', 'C', 'P'):
                # vertical moves: delta = num steps forward/backward
                tr = sr + forward * num if third == '进' else sr - forward * num
            elif piece_type == 'N':
                tc = 9 - num if side == 'red' else num - 1
                tr = sr + forward * 2 if third == '进' else sr - forward * 2
            elif piece_type == 'B':
                tc = 9 - num if side == 'red' else num - 1
                tr = sr + forward * 2 if third == '进' else sr - forward * 2
            elif piece_type == 'A':
                tc = 9 - num if side == 'red' else num - 1
                tr = sr + forward * 1 if third == '进' else sr - forward * 1
            elif piece_type == 'K':
                # King moves one step
                if third == '平':
                    tc = 9 - num if side == 'red' else num - 1
                else:
                    tr = sr + forward * 1 if third == '进' else sr - forward * 1
            else:
                raise ValueError(f"Unsupported piece type: {piece_type}")
        else:
            raise ValueError(f"Invalid action: {third}")

        return (sr, sc), (tr, tc)


    def _apply_move(self, move, side='auto', verbose=True):
        """
        Apply move, update piece_moves (append for mover, set captured piece to 0).
        Returns new_board, new_fen, new_piece_moves.
        If parsing fails, prints a nice error message instead of raw ValueError.
        """

        try:
            res = self._parse_move(move, side)
        except Exception as e:
            if verbose:
                print(f"❌ Could not parse move '{move}': {e}")
            return 

        if not res:
            if verbose:
                print(f"⚠️  Move '{move}' could not be understood — perhaps ambiguous or illegal.")
            return 

        (sr, sc), (tr, tc) = res

        if not (0 <= tr < 10 and 0 <= tc < 9):
            if verbose:
                print(f"🚫 Target out of bounds for move '{move}': {(tr, tc)}")
            return 

        mover = self.board[sr][sc]
        captured = self.board[tr][tc]

        if mover == '.':
            if verbose:
                print(f"❌ No piece at start square {sr, sc} for move '{move}'.")
            return 

        # move the piece
        self.board[tr][tc] = mover
        self.board[sr][sc] = '.'

        # find moved piece ID
        moved_pid = None
        for pid, path in self.piece_moves.items():
            if path and path != 0 and path[-1] == (sr, sc):
                moved_pid = pid
                break

        if moved_pid is None:
            for pid, path in self.piece_moves.items():
                if path and path != 0 and pid[0] == mover and path[-1] == (sr, sc):
                    moved_pid = pid
                    break

        if moved_pid is None:
            if verbose:
                print(f"⚠️  Could not find piece ID for mover {mover} at {(sr, sc)} in move '{move}'.")
                self._from_matrix()
            return 

        # update path
        if self.piece_moves[moved_pid] == 0:
            self.piece_moves[moved_pid] = [(tr, tc)]
        else:
            self.piece_moves[moved_pid].append((tr, tc))

        # handle capture
        if captured != '.':
            for pid, path in self.piece_moves.items():
                if pid == moved_pid:
                    continue
                if path and path != 0 and path[-1] == (tr, tc):
                    self.piece_moves[pid].append(('###'))
                    if verbose:
                        print(f"💥 '{captured}' captured by '{mover}' at {(tr, tc)}!")
                    break
                  
        self._from_matrix()
        self.fens.append(self.fen)

        if verbose:
            print(f"✅ Move applied: {move} | {mover} from {(sr, sc)} → {(tr, tc)}")
            print(f"   New FEN: {self.fen}")

        return


    def moves_seq(self):
        """
        Apply a full Xiangqi move list (in standard Chinese notation) to a board.

        Args:
            board: Current board state (2D list or array)
            text: Multiline text containing rounds like '1. 炮二平五，马２进３'
            
        Returns:
        
        """

        # Parse rounds
        lines = self.moves.strip().split('\n')
        rounds = []
        for line in lines:
            if not line.strip():
                continue
            try:
                num_part, moves_part = line.split('.', 1)
                round_num = int(num_part.strip())
                import re
                moves = [m.strip() for m in re.split(r'[，,\s]{1,}', moves_part.strip()) if m.strip()]
                red_move = moves[0]
                black_move = moves[1] if len(moves) > 1 else None
                rounds.append((round_num, red_move, black_move))
            except Exception as e:
                print(f"⚠️ Skipping malformed line '{line}': {e}")
                continue

        # Apply all rounds using parse_move_to_positions()
        for round_num, red_move, black_move in rounds:
            print(f"\n=== Round {round_num} ===")

            # 🔴 RED move
            try:
                self._apply_move(red_move, side='red', verbose=True)
                self.movesCHN.append(red_move)
            except Exception as e:
                print(f"❌ Red move '{red_move}' failed: {e}")

            # ⚫ BLACK move
            if black_move:
                try:
                    self._apply_move(black_move, side='black', verbose=True)
                    self.movesCHN.append(black_move)
                except Exception as e:
                    print(f"❌ Black move '{black_move}' failed: {e}")
            else:
                print("⚠️  No black move in this round.")

        print("\nFinal FEN:", self.fen)
        return

    def moves_print(self, pieces='all'):
        if pieces=='all':
            print("\nPiece move histories:")
            for pid, moves in self.piece_moves.items():
                print(pid, "→", moves)
        else:
            print("list:", [k for k in self.piece_moves if k.startswith(pieces)])
            print("Moves for that cannon:", [self.piece_moves[k] for k in self.piece_moves if k.startswith(pieces)])

    def moves_count_stats(self):

        # Initialize counters
        red_moves = 0
        black_moves = 0

        print("Moves per piece:")
        for pid, moves in self.piece_moves.items():
            side = "Red" if pid[0].isupper() else "Black"
            last_move = moves[-1]
            if last_move == "###":
                num_moves = max(0, len(moves) - 2)
            else:
                num_moves = max(0, len(moves) - 1) # subtract initial position

                if side == "Red":
                    red_moves += num_moves
                else:
                    black_moves += num_moves
            
            print(f"{pid} ({side}): {num_moves} move(s)")

        print(f"\nTotal moves — Red: {red_moves}, Black: {black_moves}")
