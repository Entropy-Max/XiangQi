import matplotlib.font_manager as fm
import os
import requests
import shutil

file_names = ["BabelStoneXiangqiColour.ttf",
              "minixianqj.ttf"]
font_path = ""

def font_download(file_name, source='github'):

    global font_path
    
    # Download font

    if source=='github':
        url = f"https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/{file_name}"
    else: 
        url = "https://www.babelstone.co.uk/Fonts/Download/BabelStoneXiangqiColour.ttf"

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)

    # Activate 
    this_font_path = font_path + '/' + file_name
    #"/usr/share/fonts/truetype/BabelStoneXiangqiColour.ttf"
   
    shutil.copy(file_name, this_font_path)

    print(f"Font downloading {file_name} ......done!")

def font_setup():
    """Check font file exists, if not then download"""

    global file_names,font_path

    # System fonts directory
    font_files = fm.findSystemFonts()
    font_path = os.path.dirname(font_files[0])
    font_names = sorted({os.path.basename(f) for f in font_files})

    for file_name in file_names:
        if (not file_name in font_names) and (not os.path.exists(file_name)):
            font_download(file_name)

    # font register 
    os.system('!fc-cache -f -v')
    os.system('!fc-list :family')
    os.system('!fc-list :family | grep -i BabelStoneColour')
               
    print("Font setup......done!")
