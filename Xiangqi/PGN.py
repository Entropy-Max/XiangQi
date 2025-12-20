from Xiangqi.common import HINTS, AXF_map_cte, AXF_map_etc, numerals_english, numerals_chinese, action_map_etc,action_map_cte

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
                if red_move[1].isdigit():
                    red_move=AXF_map_etc[red_move[0]] +\
                      numerals_english[int(red_move[1])]+\
                      action_map_etc[red_move[2]]+\
                      numerals_english[int(red_move[3])]
                elif red_move[1]=='+':
                    red_move='前'+\
                      AXF_map_etc[red_move[0]]+\
                      action_map_etc[red_move[2]]+\
                      numerals_english[int(red_move[3])]     
                elif red_move[1]=='-':
                    red_move='后'+\
                      AXF_map_etc[red_move[0]]+\
                      action_map_etc[red_move[2]]+\
                      numerals_english[int(red_move[3])]

            if len(result) == 3: 
                black_move = result[2]
                if len(black_move)==4:
                    if black_move[1].isdigit():
                        black_move = AXF_map_etc[black_move[0].lower()]+\
                            black_move[1]+\
                            action_map_etc[black_move[2]]+\
                            black_move[3]
                    elif red_move[1]=='+':
                        black_move = '前'+\
                            AXF_map_etc[black_move[0].lower()]+\
                            action_map_etc[black_move[2]]+\
                            black_move[3]
                    elif red_move[1]=='-':
                        black_move = '后'+\
                            AXF_map_etc[black_move[0].lower()]+\
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
                if red_move[0] in HINTS:
                    print("hints")
                    if red_move[0]=='前':
                        hint='+'
                    elif red_move[0]=='后':
                        hint='-'
                    else:
                        hint='='
                    red_move=AXF_map_cte[red_move[1]]+\
                        hint +\
                        action_map_cte[red_move[2]]+\
                        str(numerals_chinese[red_move[3]])
                else:
                    red_move=AXF_map_cte[red_move[0]]+\
                        str(numerals_chinese[red_move[1]])+\
                        action_map_cte[red_move[2]]+\
                        str(numerals_chinese[red_move[3]])
            else:
                print("Notation format")

            if len(result) == 3: 
                black_move = result[2]
                if len(black_move)==4:
                    if black_move[0] in HINTS:
                        print("hints")
                        if black_move[0]=='前':
                            hint='+'
                        elif black_move[0]=='后':
                            hint='-'
                        else:
                            hint='='
                        black_move = AXF_map_cte[black_move[1]]+\
                            hint+\
                            action_map_cte[black_move[2]]+\
                            str(black_move[3])
                    else:
                        black_move = AXF_map_cte[black_move[0]]+\
                            str(black_move[1])+\
                            action_map_cte[black_move[2]]+\
                            str(black_move[3])
                else:
                    print("Notation format")
                            

                self.AXF.append(round+' '+red_move+' '+black_move)

            else:
                self.AXF.append(round+' '+red_move)

        self.AXF =  '\n'.join(self.AXF)

    def CHN_flip(self):
        # experimental ... waiting for incorporation to CHN
        # can't process 前后
        
        moves_new = []

        for move in self.CHN.strip().split('\n'):
            result = move.split()
        
            round = result[0]
        
            red_move = result[1]   
            if len(red_move) == 4:
                if (red_move[0] in '马仕相'):
                    red_move=red_move[0]+\
                        numerals_english[10 - numerals_chinese[red_move[1]]] +\
                        red_move[2]+\
                        numerals_english[10 - numerals_chinese[red_move[3]]]
                else:                        
                    red_move=red_move[0]+\
                        numerals_english[10 - numerals_chinese[red_move[1]]] +\
                        red_move[2]+\
                        str(numerals_english[10 - numerals_chinese[red_move[3]]] if red_move[2] == '平' else  red_move[3]) 
                    

            if len(result) == 3: 
                black_move = result[2]
                if len(black_move) == 4:
                    if (black_move[0] in '马士象'):
                        black_move=black_move[0]+\
                            str(10 - int(black_move[1])) +\
                            black_move[2]+\
                            str(10 - int(black_move[3]))                                  
                    else:
                        black_move=black_move[0]+\
                            str(10 - int(black_move[1])) +\
                            black_move[2]+\
                            (str(10 - int(black_move[3])) if black_move[2] == '平' else  black_move[3])
                    

                moves_new.append(round+' '+red_move+' '+black_move)

            else:
                moves_new.append(round+' '+red_move)

        self.CHN =  '\n'.join(moves_new)
