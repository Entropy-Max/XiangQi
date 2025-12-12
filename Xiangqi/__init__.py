from . import font
from . import FEN
from Xiangqi.FEN import FEN

START_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r"
ENGINE_PATH = 'fairyxq'
NNUE_PATH = 'xiangqi-c07e94a5c7cb.nnue'

__all__ = ["FEN","START_FEN","ENGINE_PATH","NNUE_PATH"]

font.font_setup()


