

import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF


#import handle_db

baseDir = os.path.dirname(os.path.realpath(__file__))


def generate(callsign, out_path, lang="en"):
    #print(baseDir)

    backgroundImg = os.path.join(baseDir, "raw_diploma", "diploma_002.png") 
    font = os.path.join(baseDir, "raw_diploma", "font", "Gontserrat-Regular.ttf")       
    
    background = Image.open(backgroundImg)     

    
    fontSize = 150
    fontColor = (0,0,0)

    W, H = background.size
    #print("img size: ", W, H)

    I1 = ImageDraw.Draw(background)
    myFont = ImageFont.truetype(font, fontSize)
    I1.text((W//2, 350), callsign.upper(), anchor="mm", font=myFont, fill=fontColor)

    
    fileDir = os.path.dirname(out_path)
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    
    background.save(out_path)
    
    #background.save(os.path.join(fileDir, f"diploma_{callsign.lower()}_{lang}.pdf"))
    #background.save(os.path.join(fileDir, f"diploma_{callsign}.png"))
    
    
    return ""

def generate_fpdf(callsign, out_path, lang="en"):

    backgroundImg = os.path.join(baseDir, "raw_diploma", "diploma_007.png") 
    #print("backgroundImg", backgroundImg)

    if "_" in callsign:
        callsign = callsign.replace("_", "/")

    W, H = 297, 210


    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page(orientation = 'L')
    pdf.image(backgroundImg, x=0, y=0, w=W, h=H)
    
    fontPath = os.path.join(baseDir, "raw_diploma", "font", "Cinzel", "static", "Cinzel-SemiBold.ttf")
    pdf.add_font("myfont", "", fontPath)
    pdf.set_font('myfont', size=90)
    pdf.set_text_color(142, 25, 25)
    strWidth = pdf.get_string_width(callsign)
    print("strWidth", strWidth)

    pdf.set_xy(W/2-strWidth/2, 34)
    pdf.cell(0, 0, callsign.upper())

    pdf.set_title("HG25CCS")
    pdf.output(out_path)

if __name__ == "__main__":
    import time

    '''startTime = time.time()
    generate("ha1mp", "./test_pil.pdf", "en")
    print("time: ", time.time() - startTime)'''


    startTime = time.time()
    generate_fpdf("ha1mp", "./tmp/test_diploma.pdf", "en")
    print("time: ", time.time() - startTime)