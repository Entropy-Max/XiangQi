import os
import requests
from Xiangqi import *

def _engine_download(ENGINE_PATH, source="xiangqi"):
  
    file_name = os.path.basename(ENGINE_PATH)
  
    if source.lower()=='xiangqi':
        url = f"https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/{file_name}"
    else:
        url = "https://github.com/fairy-stockfish/Fairy-Stockfish/releases/latest/download/fairy-stockfish-largeboard_x86-64"

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)
    
    print(f"{file_name} downloading ...... done!")

def engine_setup(ENGINE_PATH): 
  
  if not os.path.exists(ENGINE_PATH):
      _engine_download(ENGINE_PATH)
  
  # Make it executable
  file_name = os.path.basename(ENGINE_PATH)
  os.system(f"chmod +x {file_name}")
  
  print(f"{file_name} engine starting up ...... done!")
  
