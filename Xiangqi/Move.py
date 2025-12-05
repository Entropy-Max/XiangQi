from PIL import Image

from Xiangqi.FEN import FEN
import re

red_pieces = '车马炮帅仕相兵'
black_pieces = '車馬砲将士象卒'
PIECES = red_pieces + black_pieces

chinese_nums = '一二三四五六七八九'
arabic_nums = '123456789'
NUMS = chinese_nums + arabic_nums

HINTS = '前中后一二三四五'
ACTIONS = '进退平'

numerals_chinese = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9
}

numerals_english = {
    1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
    6: '六', 7: '七', 8: '八', 9: '九'
}

# Piece names map
## Chinese to English
piece_map_cte = {
    # Red (Uppercase)
    '车': 'R', '马': 'N', '炮': 'C', '相': 'B', '仕': 'A', '帅': 'K', '帥': 'K', '兵': 'P',
    # Black (Lowercase)
    '車': 'r', '馬': 'n', '砲': 'c', '象': 'b', '士': 'a', '将': 'k', '將': 'k', '卒': 'p'
}

## English to Chinese
piece_map_etc = {
    #  Red (Uppercase)
    "K": "帅", "A": "仕", "B": "相", "N": "马", "R": "车", "C": "炮", "P": "兵",
    # Black (Lowercase)
    "k": "将", "a": "士", "b": "象", "n": "马", "r": "车", "c": "炮", "p": "卒"
}


# Numerals
## Chinese to English
def numerals_cte(x):
    if x in numerals_chinese:
        return numerals_chinese[x]
    if x.isdigit():
        return int(x)
    raise ValueError(f"Invalid numeral: {x}")

## English to Chinese
def numerals_etc(x):
    if isinstance(x,int):
        x=str(x)

    if x.isdigit():
        return numerals_english[int(x)]
    raise ValueError("numerals_etc")


class Move(FEN):

    def __init__(self,fen,moves):
        super().__init__(fen)
        self.moves = moves
        self.movesCHN=[]
        self.fens=[self.fen]
        self.piece_counts = {}
        self.piece_moves = {}
        self.moves_etc()

    # UCI moves

    @staticmethod
    def _parse_move(move):

        if not(len(move) in (4,5,6)):
            raise ValueError("length of move must be 4!")

        m = re.fullmatch(r"([a-i])(10|[1-9])([a-i])(10|[1-9])", move)
        if not m:
            raise ValueError("Regular Expressions!")

        sx = ord(m.group(1)) - ord("a")
        sy = 10 - int(m.group(2))
        tx = ord(m.group(3)) - ord("a")
        ty = 10 - int(m.group(4))

        return sx,sy,tx,ty


    def _apply_move(self, sx,sy,tx,ty):

        piece = self.board[sy][sx]

        if piece == ".":
            return f'**{turn_red}**no piece**'

        is_red = piece.isupper()
        name = piece_map_etc[piece]

        start_file = numerals_etc(9-sx) if is_red else str(sx+1)
        end_file = numerals_etc(9-tx)if is_red else str(tx+1)

        dx = tx - sx
        dy = ty - sy

        notation = ""

        if piece.upper() in ["N","B","A"]:  # Knight, Elephant, Advisor
            # Always show starting file + direction + target file
            direction = "进" if (dy < 0 and is_red) or (dy > 0 and not is_red) else "退"
            notation = f"{name}{start_file}{direction}{end_file}"
        else:  # Rook, Cannon, Pawn, King
            if sx == tx:  # vertical
                if is_red:
                    direction = "进" if ty < sy else "退"
                else:
                    direction = "进" if ty > sy else "退"
                steps = abs(ty - sy)
                if is_red: steps = numerals_english[steps]
                notation = f"{name}{start_file}{direction}{steps}"
            elif sy == ty:  # horizontal
                notation = f"{name}{start_file}平{end_file}"
            else:  # uncommon diagonal (King in palace)
                if is_red:
                    direction = "进" if ty < sy else "退"
                else:
                    direction = "进" if ty > sy else "退"
                notation = f"{name}{start_file}{direction}{end_file}"

        # Update board
        self.board[sy][sx] = "."
        self.board[ty][tx] = piece

        self._from_matrix()
        self.fens.append(self.fen)

        # Alternate side
        self.turn_red = not self.turn_red

        return notation


    def moves_etc(self):

        self.movesCHN = []

        for mv in self.moves:
            try:
                sx,sy,tx,ty = self._parse_move(mv)
                notation = self._apply_move(sx,sy,tx,ty)
                self.movesCHN.append(notation)

            except Exception:
                self.movesCHN.append('****')
                self.turn_red = not self.turn_red
                continue

        self.movesCHN =' '.join(self.movesCHN)


    def draw_all(self):
        frames=[]
        for i, fen in enumerate(self.fens):
            img = FEN(fen).draw()
            frames.append(img)

        import glob

        # save as gif
        frames[0].save(
            "animation.gif",
            save_all=True,
            append_images=frames[1:],
            duration=2000,   # milliseconds per frame (0.5s)
            loop=0          # loop forever
        )
