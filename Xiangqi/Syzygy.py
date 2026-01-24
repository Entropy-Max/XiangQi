from Xiangqi import *

def heatmap(engine,BASE_FEN_0,BASE_FEN_1,piece,NNUE=None):

    if NNUE:
        base_eval = engine._nnue_eval_fen(BASE_FEN_0)
    else:
        base_eval = engine._eval_fen(BASE_FEN_0)

    if base_eval is None:
        raise ValueError("Base FEN not evaluable by NNUE")

    # heatmap[rank][file] # rank 0..9, file 0..8

    heatmap_data = [[0.0 for _ in range(9)] for _ in range(10)]

    for rank in range(10):
        for file in range(9):
            fen=FEN(BASE_FEN_1)
            fen._to_matrix()

            r = 9 - rank

            if fen.board[r][file]== '.':
                fen.board[r][file]=piece

                fen._from_matrix()

                if NNUE:
                    v = engine._nnue_eval_fen(fen.fen)-base_eval
                else:
                    v = engine._eval_fen(fen.fen)-base_eval
                    
                if v is None:
                    raise ValueError("Dynamic FEN not evaluable")
            else:
                v = 0

            heatmap_data[rank][file] = v
          
    return heatmap_data
