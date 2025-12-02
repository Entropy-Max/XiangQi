# Download manually 
#!wget -O BabelStoneXiangqiColour.ttf https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/BabelStoneXiangqiColour.ttf

def font_download(source='github'):
    """Download Font BabelStone Xiangqi Colour"""

    import os
    import requests

    # Download font

    if source=='github':
        url = "https://raw.githubusercontent.com/Entropy-Max/XiangQi/main/BabelStoneXiangqiColour.ttf"
    else: 
        url = "https://www.babelstone.co.uk/Fonts/Download/BabelStoneXiangqiColour.ttf"

    file_name = "BabelStoneXiangqiColour.ttf"

    r = requests.get(url)
    with open(file_name, "wb") as f:
        f.write(r.content)

    print("Font downloading......ready")

def font_setup():
    """Check font file exists, if not then download"""

    import os
    import shutil

    file_name = "BabelStoneXiangqiColour.ttf"

    if not os.path.exists(file_name): 
        font_download()
       
    # Activate 

    font_path = "/usr/share/fonts/truetype/BabelStoneXiangqiColour.ttf"

    shutil.copy(file_name, font_path)

    os.system('!fc-cache -f -v')
    os.system('!fc-list :family')
    os.system('!fc-list :family | grep -i BabelStoneColour')

    print("Font setup......ready")
