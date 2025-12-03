from PIL import Image, ImageDraw, ImageFont
from IPython.display import display

# FEN (Forsyth-Edwards Notation)
# https://xiangqiboard.com/
# https://xiangqiboard.com/editor
# https://xqbase.com/tools/xqviewer.htm

class FEN:
    def __init__(self, fen):
        self.fen = fen   # attribute

    def __str__(self):
        return f"FEN(fen={self.fen})"

    def flip_lr(self):

        ranks = self.fen.split('/')

        self.fen = '/'.join(rank[::-1] for rank in ranks)

    def flip_case(self):

        self.fen = ''.join(ch.lower() if ch.isupper() else ch.upper() if ch.islower() else ch for ch in self.fen)

    def set_red_top(self):

        ranks = self.fen.split('/')

        red_king_rank = next((i for i, r in enumerate(ranks) if 'K' in r), None)
        black_king_rank = next((i for i, r in enumerate(ranks) if 'k' in r), None)

        # Decide which side is on top
        if red_king_rank is not None and black_king_rank is not None:
            if red_king_rank < black_king_rank:
                self.fen = self.fen
            else:
                self.fen = self.fen[::-1]
        else:
            print("Could not determine (no kings found).")

    def set_red_bottom(self):

        ranks = self.fen.split('/')

        red_king_rank = next((i for i, r in enumerate(ranks) if 'K' in r), None)
        black_king_rank = next((i for i, r in enumerate(ranks) if 'k' in r), None)

        # Decide which side is on top
        if red_king_rank is not None and black_king_rank is not None:
            if red_king_rank > black_king_rank:
                self.fen =  self.fen
            else:
                self.fen =  self.fen[::-1]
        else:
            print("Could not determine (no kings found).")

    def print(self):

        board= fen_to_matrix(self.fen)
        for r in board:
            print(' '.join(r))

    def draw(self): 

        # Board config
        cell_size = 60
        cols, rows = 9, 10
        width = cell_size * cols
        height = cell_size * rows
        bg_color = "white"
        line_color = "black"

        # Piece map: (Unicode code point, color)

        piece_map = {
            'K': (0x1FA60, 'red'),   # 帅
            'A': (0x1FA61, 'red'),   # 仕
            'B': (0x1FA62, 'red'),   # 相
            'N': (0x1FA63, 'red'),   # 马
            'R': (0x1FA64, 'red'),   # 车
            'C': (0x1FA65, 'red'),   # 炮
            'P': (0x1FA66, 'red'),   # 兵

            'k': (0x1FA67, 'black'), # 将
            'a': (0x1FA68, 'black'), # 士
            'b': (0x1FA69, 'black'), # 象
            'n': (0x1FA6A, 'black'), # 马
            'r': (0x1FA6B, 'black'), # 车
            'c': (0x1FA6C, 'black'), # 砲
            'p': (0x1FA6D, 'black'), # 卒
        }

        # Board map

        board_map = [
            (0,3,0xE00A),
            (0,6,0xE00A),
            (8,3,0xE00B),
            (8,6,0xE00B),
            (1,2,0xE009),
            (7,2,0xE009),
            (1,7,0xE009),
            (7,7,0xE009),
            (2,3,0xE009),
            (4,3,0xE009),
            (6,3,0xE009),
            (2,6,0xE009),
            (4,6,0xE009),
            (6,6,0xE009)
        ]
    
        font_path = "BabelStoneXiangqiColour.ttf" 
        font_piece = ImageFont.truetype(font_path, 48)

        # Create blank image
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Grid lines
        for i in range(rows):
            y = i * cell_size + cell_size // 2
            draw.line([(cell_size // 2, y), (width - cell_size // 2, y)], fill=line_color, width=3)

        for j in range(cols):
            x = j * cell_size + cell_size // 2
            if j == 0 or j == cols - 1:
                draw.line([(x, cell_size // 2), (x, height - cell_size // 2)], fill=line_color, width=3)
            else:
                draw.line([(x, cell_size // 2), (x, 4.5 * cell_size)], fill=line_color, width=3)
                draw.line([(x, 5.5 * cell_size), (x, height - cell_size // 2)], fill=line_color, width=3)

        # Palace diagonals
        def draw_palace(x0, y0):
            draw.line([(x0, y0), (x0 + 2*cell_size, y0 + 2*cell_size)], fill=line_color, width=2)
            draw.line([(x0 + 2*cell_size, y0), (x0, y0 + 2*cell_size)], fill=line_color, width=2)

        draw_palace(cell_size*3 + cell_size//2, cell_size//2)
        draw_palace(cell_size*3 + cell_size//2, cell_size*7 + cell_size//2)

        # Board stars
        for col, row, codepoint in board_map:
            x = col * cell_size + cell_size // 2
            y = row * cell_size + cell_size // 2

            draw.text((x, y), chr(codepoint), font=font_piece, fill='black', anchor="mm")

        # Example FEN

        ranks = self.fen.split()[0].split('/')

        # Draw pieces with circle + color
        for row_idx, row in enumerate(ranks):
            col_idx = 0
            for ch in row:
                if ch.isdigit():
                    col_idx += int(ch)
                else:
                    piece_char, color = piece_map.get(ch, ('?', 'gray'))
                    x = col_idx * cell_size + cell_size // 2
                    y = row_idx * cell_size + cell_size // 2

                    # Draw circle
                    radius = cell_size * 0.35
                    bbox = [x - radius, y - radius, x + radius, y + radius]
                    draw.ellipse(bbox, outline=color, fill='white', width=2)

                    # Draw piece text
                    draw.text((x, y), chr(piece_char), font=font_piece, fill=color, anchor="mm")

                    col_idx += 1

        display(img)

    def draw_new(self,orientation='h'):

        img1 = self.draw(self.set_red_bottom(self.fen))
        img2 = self.draw(self.set_red_top(self.fen))

        if orientation=='h':
            # Paste both images side by side
            new_img = Image.new('RGB', (img1.width*2, img1.height))
            new_img.paste(img1, (0, 0))
            new_img.paste(img2, (img1.width, 0))
        else:
            new_img = Image.new('RGB', (img1.width, img1.height*2))
            new_img.paste(img1, (0, 0))
            new_img.paste(img2, (0, img1.height))

        display(new_img)
