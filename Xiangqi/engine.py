import os
import requests

engine_path = '/content/fairyxq'
file_name = os.path.basename(engine_path)

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

  global engine_path
  
  if not os.path.exists(engine_path):
      engine_download()
  
  # Make it executable
  os.system("chmod +x {file_name}")
  print("Fairy Stockfish engine starting up ...... done!")
  
