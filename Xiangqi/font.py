import matplotlib.font_manager as fm
import os
import requests
import shutil

def font_download(source='github'):
    """Download Font BabelStone Xiangqi Colour"""
    
    # Download font

    if source=='github':
        url = "https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/BabelStoneXiangqiColour.ttf"
    else: 
        url = "https://www.babelstone.co.uk/Fonts/Download/BabelStoneXiangqiColour.ttf"

    file_name = "BabelStoneXiangqiColour.ttf"

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)

    # Activate 
    font_path = "/usr/share/fonts/truetype/BabelStoneXiangqiColour.ttf"
    shutil.copy(file_name, font_path)

    os.system('!fc-cache -f -v')
    os.system('!fc-list :family')
    os.system('!fc-list :family | grep -i BabelStoneColour')
        
    print("Font downloading......done!")

def font_setup():
    """Check font file exists, if not then download"""
 
    file_name = "BabelStoneXiangqiColour.ttf"

    # System fonts directory
    font_files = fm.findSystemFonts()
    font_names = sorted({os.path.basename(f) for f in font_files})

    if (not file_name in font_names) and (not os.path.exists(file_name)):
        font_download()
       
    print("Font setup......done!")
