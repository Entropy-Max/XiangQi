from Xiangqi.common import AXF_map_cte, AXF_map_etc, numerals_english, numerals_chinese, action_map_etc,action_map_cte

class PGN():
    def __init__(self,moves):
        self.AXF = moves
        self.CHN = moves
    
    def AXF_CHN(self):

        self.CHN = []

        for move in self.AXF.strip().split('\n'):
            result = move.split()
            round = result[0]
            red_move = result[1]   
            if len(red_move)==4:

                red_move=AXF_map_etc[red_move[0]]+\
                    numerals_english[int(red_move[1])]+\
                    action_map_etc[red_move[2]]+\
                    numerals_english[int(red_move[3])]

            if len(result) == 3: 
                black_move = result[2]
                black_move = AXF_map_etc[black_move[0].lower()]+\
                    black_move[1]+\
                    action_map_etc[black_move[2]]+\
                    black_move[3]

                self.CHN.append(round+' '+red_move+' '+black_move)

            else:
                self.CHN.append(round+' '+red_move)

        self.CHN =  '\n'.join(self.CHN)
          
    def CHN_AXF(self):

        self.AXF = []

        for move in self.CHN.strip().split('\n'):
            result = move.split()
        
            round = result[0]
        
            red_move = result[1]   
            if len(red_move)==4:

                red_move=AXF_map_cte[red_move[0]]+\
                    str(numerals_chinese[red_move[1]])+\
                    action_map_cte[red_move[2]]+\
                    str(numerals_chinese[red_move[3]])

            if len(result) == 3: 
                black_move = result[2]
                black_move = AXF_map_cte[black_move[0]]+\
                    str(black_move[1])+\
                    action_map_cte[black_move[2]]+\
                    str(black_move[3])

                self.AXF.append(round+' '+red_move+' '+black_move)

            else:
                self.AXF.append(round+' '+red_move)

        self.AXF =  '\n'.join(self.AXF)

    def CHN_flip(self):

        moves_new = []

        for move in self.CHN.strip().split('\n'):
            result = move.split()
        
            round = result[0]
        
            red_move = result[1]   
            if len(red_move)==4:

                red_move=red_move[0]+\
                    str(10 - numerals_chinese[red_move[1]]) if red_move[1] == '平' else  str(numerals_chinese[red_move[1]]) +\
                    str(numerals_chinese[red_move[2]])+\
                    str(10 - numerals_chinese[red_move[1]]) if red_move[1] == '平' else  str(numerals_chinese[red_move[1]]) 
                    

            if len(result) == 3: 
                black_move = result[2]
                black_move=black_move[0]+\
                    str(10 - numerals_chinese[black_move[1]]) if black_move[1] == '平' else  str(numerals_chinese[black_move[1]]) +\
                    str(numerals_chinese[black_move[2]])+\
                    str(10 - numerals_chinese[black_move[1]]) if black_move[1] == '平' else  str(numerals_chinese[black_move[1]]) 
                    

                moves_new.append(round+' '+red_move+' '+black_move)

            else:
                moves_new.append(round+' '+red_move)

        self.CHN =  '\n'.join(moves_new)
