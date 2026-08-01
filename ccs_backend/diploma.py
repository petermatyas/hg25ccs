

import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF


#import handle_db

baseDir = os.path.dirname(os.path.realpath(__file__))


def generate(callsign, out_path, lang="en"):
    #print(baseDir)

    backgroundImg = os.path.join(baseDir, "raw_diploma", "diploma.jpg") 
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

    backgroundImg = os.path.join(baseDir, "raw_diploma", "HG25CCS_Diploma.png") 
    #print("backgroundImg", backgroundImg)

    if "_" in callsign:
        callsign = callsign.replace("_", "/")

    W, H = 297, 210


    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page(orientation = 'L')
    pdf.image(backgroundImg, x=0, y=0, w=W, h=H)
    
    fontPath = os.path.join(baseDir, "raw_diploma", "font", "Cinzel", "static", "Cinzel-SemiBold.ttf")
    pdf.add_font("myfont", "", fontPath)
    pdf.set_font("myfont", size=60)
    pdf.set_text_color(142, 25, 25)
    strWidth = pdf.get_string_width(callsign)
    print("strWidth", strWidth)

    pdf.set_xy(W/2-strWidth/2, 30)
    pdf.cell(0, 0, callsign.upper())

    pdf.set_title("HG25CCS")

    # A cél mappa (pl. .../diplomas) nem feltétlenül létezik – az fpdf nem
    # hozza létre a hiányzó szülőkönyvtárat, ezért itt biztosítjuk.
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf.output(out_path)

def generate_charset_preview(out_path, font_size=80, cols=8):
    """Egy oldalas betűkészlet-minta a diploma betűstílusával.

    Ugyanazzal a betűvel és színnel (Cinzel-SemiBold, 142,25,25), mint a
    diploma-hívójel, egyetlen A4 fekvő oldalra kirajzolja az angol ábécé összes
    (nagy)betűjét, a számjegyeket és a '/' jelet – rácsba rendezve, hogy elférjen.
    Hasznos a betűtípus megjelenésének ellenőrzéséhez.
    """
    import string
    import math

    W, H = 297, 210  # A4 fekvő, mm

    # Az angol ábécé (a diploma is nagybetűvel ír), a számok és a '/' jel.
    chars = list(string.ascii_uppercase) + list(string.digits) + ["/"]

    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page(orientation='L')

    # A kijelölt rész betűstílusa: Cinzel-SemiBold, adott méret, sötétvörös.
    fontPath = os.path.join(baseDir, "raw_diploma", "font", "Cinzel", "static", "Cinzel-SemiBold.ttf")
    pdf.add_font("myfont", "", fontPath)
    pdf.set_font("myfont", size=font_size)
    pdf.set_text_color(142, 25, 25)

    # Rács kiszámítása, hogy minden karakter elférjen egy oldalon.
    margin = 15
    rows = math.ceil(len(chars) / cols)
    cellW = (W - 2 * margin) / cols
    cellH = (H - 2 * margin) / rows

    for idx, ch in enumerate(chars):
        r = idx // cols
        c = idx % cols
        # A cella közepe; a cell(…, h=0) a szöveget az y-ra függőlegesen középre teszi.
        cx = margin + c * cellW + cellW / 2
        cy = margin + r * cellH + cellH / 2
        strWidth = pdf.get_string_width(ch)
        pdf.set_xy(cx - strWidth / 2, cy)
        pdf.cell(0, 0, ch)

    pdf.set_title("HG25CCS betűkészlet minta")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    pdf.output(out_path)
    return out_path


if __name__ == "__main__":
    import time

    '''startTime = time.time()
    generate("ha1mp", "./test_pil.pdf", "en")
    print("time: ", time.time() - startTime)'''


    startTime = time.time()
    generate_fpdf("qha1nbs/p", "./tmp/test_diploma.pdf", "en")
    print("time: ", time.time() - startTime)

    #generate_charset_preview("./tmp/font.pdf", font_size=80, cols=8)