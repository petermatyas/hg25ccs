import os
import datetime

from fpdf import FPDF
import textwrap

import config

baseDir = os.path.dirname(os.path.realpath(__file__))


def getActivationCallsign():
    """Az aktiválás hívójele a konfigurációból (CCS_ACTIVATION_CALLSIGN).

    Ez kerül a lap fejlécébe, a morze sorba, a PDF címébe, és ezt kapja az
    operátor mező is, ha a naplóbeli operátor nem azonosítható.
    """
    return config.getActivationCallsign()


MORSE_CODES = {
    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",   "E": ".",
    "F": "..-.",  "G": "--.",   "H": "....",  "I": "..",    "J": ".---",
    "K": "-.-",   "L": ".-..",  "M": "--",    "N": "-.",    "O": "---",
    "P": ".--.",  "Q": "--.-",  "R": ".-.",   "S": "...",   "T": "-",
    "U": "..-",   "V": "...-",  "W": ".--",   "X": "-..-",  "Y": "-.--",
    "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
    "/": "-..-.",
}


def toMorse(text):
    """A hívójel morze alakja (a lap alján futó díszítősor).

    Az ismeretlen karaktereket kihagyja, a betűk közé szóköz kerül.
    """
    return " ".join(MORSE_CODES[ch] for ch in str(text).upper() if ch in MORSE_CODES)


def getOperators():
    """A helyi operátorok listája a beállításokból (config.getOperators())."""
    return config.getOperators()

RED = (142, 25, 25)
SILVER = (192, 192, 192)


# A naplófeldolgozó a fel nem ismert mezőket hibajelzéssel tölti fel
# ('error', 'error2', 'missing', 'nem ismert sáv: ...', '[ERROR] date:...').
# Ezek nem kerülhetnek rá a QSL lapra – az ilyen mező üresen marad.
ERROR_VALUES = ("error", "error2", "missing", "none", "??", "")
ERROR_PREFIXES = ("[error]", "nem ismert")


def cleanValue(value):
    """A mező értéke, ha értelmes; hibajelzés esetén üres szöveg."""
    if value is None:
        return ""

    text = str(value).strip()
    if text.lower() in ERROR_VALUES:
        return ""
    if text.lower().startswith(ERROR_PREFIXES):
        return ""
    return text


def qsoDateTime(timestamp):
    """A QSO időbélyegéből (dátum, idő) szövegpár; hibás értéknél két üres."""
    try:
        dt = datetime.datetime.fromtimestamp(int(timestamp), datetime.timezone.utc)
    except (TypeError, ValueError):
        # A feldolgozó szöveges hibajelzést is tehet az időbélyeg helyére.
        return "", ""
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")


def write(x,y, text):
    pass


def addCell(pdf,x,y,w,h,text):
    pdf.set_xy(x,y)
    pdf.cell(w=w, h=h, txt=text, border=1, ln=0, align="c")
    return x+w, y+h

def generate_fpdf(out_path, data):
    W, H = 140, 90


    pdf = FPDF('L', 'mm', (H, W))
    pdf.set_margin(0)
    pdf.add_page(orientation = 'L')


    fontPath = os.path.join(baseDir, "raw_diploma", "font", "Cinzel", "static", "Cinzel-SemiBold.ttf")
    #fontPath = os.path.join(baseDir, "raw_diploma", "font", "Cinzel", "static", "Cinzel-Regular.ttf")
    pdf.add_font("myfont", "", fontPath)
    pdf.set_font('myfont', size=10)
    pdf.set_text_color(142, 25, 25)
    #strWidth = pdf.get_string_width(callsign)
    #print("strWidth", strWidth)


    pdf.set_text_color(SILVER)
    pdf.set_font('myfont', size=30)
    pdf.set_xy(0,0)
    pdf.set_fill_color(RED)
    activationCallsign = getActivationCallsign().upper()
    pdf.cell(w=0, h=20, txt=activationCallsign, border=0, ln=0, align="c", fill=True)

    imagePath = os.path.join(baseDir, "raw_diploma", "savaria_karneval_logo_2.png")
    pdf.image(name=imagePath, x=110, y=2, w=15, h=15)

    pdf.set_text_color(RED)
    pdf.set_font('myfont', size=10)

    station = config.getStation()
    pdf.set_xy(15,30)
    pdf.cell(w=0, h=0, txt=f"ITU: {station['itu']}", border=0, ln=0, align="l")
    pdf.set_xy(65,30)
    pdf.cell(w=0, h=0, txt=f"QTH: {station['qth']}", border=0, ln=0, align="l")
    pdf.set_xy(15,35)
    pdf.cell(w=0, h=0, txt=f"CQ:  {station['cq']}", border=0, ln=0, align="l")
    pdf.set_xy(65,35)
    pdf.cell(w=0, h=0, txt=f"LOC: {station['locator']}", border=0, ln=0, align="l")

    # Az operátorok a beállításokból kisbetűvel jönnek, a naplókban viszont
    # vegyesen szerepelnek – ezért kis/nagybetűtől függetlenül hasonlítunk.
    operators = [i.lower() for i in getOperators()]
    local_operator = cleanValue(data.get("local_operator"))
    if local_operator.lower() not in operators:
        local_operator = getActivationCallsign()
    pdf.set_xy(15,58)
    # A megtisztított értéket írjuk ki: eddig a nyers mező ment a lapra, így az
    # ismeretlen operátorra beállított aktiválási hívójel sosem érvényesült.
    pdf.cell(w=0, h=0, txt=f"Operator: {local_operator}", border=0, ln=0, align="l")
    pdf.set_xy(65,58)
    pdf.cell(w=0, h=0, txt=f"TNX 73!", border=0, ln=0, align="l")


    cellHeight = 5
    tableX = 15
    tableY = 40
    x2, y2 = addCell(pdf, tableX, tableY, 25,  cellHeight, "To radio")
    x2, y2 = addCell(pdf, x2, tableY, 25, cellHeight, "Date")
    x2, y2 = addCell(pdf, x2, tableY, 15, cellHeight, "UTC")
    x2, y2 = addCell(pdf, x2, tableY, 15,  cellHeight, "Band")
    x2, y2 = addCell(pdf, x2, tableY, 15,  cellHeight, "Mode")
    x2, y2 = addCell(pdf, x2, tableY, 15,  cellHeight, "RST")

    callsign = cleanValue(data.get("callsign"))
    if "_" in callsign:
        callsign = callsign.replace("_", "/")

    qsoDate, qsoTime = qsoDateTime(data.get("timestamp"))

    x2, y2 = addCell(pdf, tableX, tableY+cellHeight, 25,  cellHeight, callsign)
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 25, cellHeight, qsoDate)
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15, cellHeight, qsoTime)
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15,  cellHeight, cleanValue(data.get("band")))
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15,  cellHeight, cleanValue(data.get("mode")))
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15,  cellHeight, cleanValue(data.get("rst_received")))

    

    pdf.set_xy(5, 67)
    pdf.set_font('myfont', size=7)
    pdf.set_char_spacing(9)
    pdf.cell(w=W-10, h=0, text=toMorse(activationCallsign), border=0, ln=0, align="c")
    pdf.set_char_spacing(0)

    pdf.set_xy(5,70)
    pdf.set_font('myfont', size=6)
    wrapper = textwrap.TextWrapper(width=90)
    raw_text = "The Savaria Historical Carnival is organized every year in August by the city of Szombathely. During this period, the town centre takes visitors on a journey to the past. Throughout the event, countless colorful programs are offered to visitors. Stalls offering handmade products, concerts, gastronomic experiences, and child-friendly programs welcome the guests. The highlight of the Carnival is the costume parade (in the evening), which brings to life the 2,000-year-old history of Szombathely (Savaria).\nFurther information on the official website of the Carnival: www.karnevalsavaria.hu"
    pdf.multi_cell(w=W-10, h=2.5, txt=raw_text, border=0, align="j")


    pdf.line(0,0,0,H)
    pdf.line(0,0,W,0)
    pdf.line(W,0,W,H)
    pdf.line(0,H,W,H)

    pdf.set_title(activationCallsign.upper())


    fileDir = os.path.dirname(out_path)
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    pdf.output(out_path)

if __name__ == "__main__":
    data = {'band': '2m', 'mode': 'SSB', 'timestamp': 1784065936, 'qth': 'jn87if', 'rst_sent': '59', 'rst_received': '59', 'local_operator': 'HA1NBS', 'upload_timestamp_utc': 1753472357, 'uploaded_filename': 'ha1nb_URHOB_MIX_144_MHz.edi', 'callsign': 'ha1mp'}
    generate_fpdf("./tmp/test_qsl.pdf", data)









