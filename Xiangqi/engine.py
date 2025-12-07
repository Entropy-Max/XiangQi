import os
import requests

file_name = os.path.basename(ENGINE_PATH)

def engine_download(source="xiangqi"):
  
    global file_name
  
    if source.lower()=='xiangqi':
        url = "https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/fairyxq"
    else:
        url = "https://github.com/fairy-stockfish/Fairy-Stockfish/releases/latest/download/fairy-stockfish-largeboard_x86-64"

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)
    
    print("Fairy Stockfish downloading ...... done!")

def engine_setup():

  global ENGINE_PATH
  
  if not os.path.exists(ENGINE_PATH):
      engine_download()
  
  # Make it executable
  os.system(f"chmod +x {file_name}")
  print("Fairy Stockfish engine starting up ...... done!")
  
