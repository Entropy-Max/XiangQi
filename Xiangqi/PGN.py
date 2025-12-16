from common import piece_map_etc, numerals_english, action_map_etc

def AXF_CHN(moves):

    move_new = []

    for move in moves.strip().split('\n'):
        result = move.split()
        round = result[0]
        red_move = result[1]   
        if len(red_move)==4:

            red_move=piece_map_etc[red_move[0]]+\
     numerals_english[int(red_move[1])]+\
     action_map_etc[red_move[2]]+\
     numerals_english[int(red_move[3])]

        if len(result) == 3: 
            black_move = result[2]
            black_move = piece_map_etc[black_move[0].lower()]+\
     black_move[1]+\
     action_map_etc[black_move[2]]+\
     black_move[3]

            move_new.append(round+' '+red_move+' '+black_move)

        else:
            move_new.append(round+' '+red_move)

    return '\n'.join(move_new)
          
