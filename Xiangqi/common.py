# FEN
START_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r"

# engine 

ENGINE_PATH = 'fairyxq'
NNUE_PATH = 'xiangqi-c07e94a5c7cb.nnue'

# moves

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
