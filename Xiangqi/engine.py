# download engine and nnue weights 

import os
from urllib.parse import urlparse
import requests
from Xiangqi import *

def engine_setup(backend="fairyxq"): 

    if not os.path.exists(backend):
        if backend.lower()=='fairyxq':
            url = ["https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/fairyxq"]
            #url = ["https://github.com/fairy-stockfish/Fairy-Stockfish/releases/latest/download/fairy-stockfish-largeboard_x86-64"]
        elif backend.lower()=='stockfishnnue':
            url=[]
        elif backend.lower()=='pikafish':
            print("Pikafish requires NNUE net file!")
            url = ["https://github.com/official-pikafish/Networks/releases/download/master-net/pikafish.nnue",
                "https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/pikafish"]

        for each in url:
            r = requests.get(each,stream=True)
            r.raise_for_status()
            file_name= os.path.basename(urlparse(each).path)
            with open(file_name, "wb") as f:
                f.write(r.content)
            print(f"{file_name} downloading ...... done!")

    # Make it executable
    file_name = os.path.basename(backend)
    os.system(f"chmod +x {file_name}")
  
    print(f"{file_name} engine starting up ...... done!")
  
