import os
import datetime

from fpdf import FPDF
import textwrap

baseDir = os.path.dirname(os.path.realpath(__file__))

RED = (142, 25, 25)
SILVER = (192, 192, 192)


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
    pdf.cell(w=0, h=20, txt="HG25CCS", border=0, ln=0, align="c", fill=True)

    imagePath = os.path.join(baseDir, "raw_diploma", "savaria_karneval_logo_2.png")
    pdf.image(name=imagePath, x=110, y=2, w=15, h=15)

    pdf.set_text_color(RED)
    pdf.set_font('myfont', size=10)

    pdf.set_xy(15,30)
    pdf.cell(w=0, h=0, txt="ITU: 28", border=0, ln=0, align="l")
    pdf.set_xy(65,30)
    pdf.cell(w=0, h=0, txt="QTH: SZOMBATHELY, HUNGARY", border=0, ln=0, align="l")
    pdf.set_xy(15,35)
    pdf.cell(w=0, h=0, txt="CQ:  15", border=0, ln=0, align="l")
    pdf.set_xy(65,35)
    pdf.cell(w=0, h=0, txt="LOC: JN87GF", border=0, ln=0, align="l")

    operators = ["HA1LS", "HA1MP", "HA1NB", "HA1NBS", "HA1WD", "HA1YA", "HA1WA"]
    local_operator = data["local_operator"]
    if not local_operator.upper() in operators:
        local_operator = "hg25ccs"
    pdf.set_xy(15,58)
    pdf.cell(w=0, h=0, txt=f"Operator: {data["local_operator"]}", border=0, ln=0, align="l")
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

    callsign = data["callsign"]
    if "_" in callsign:
        callsign = callsign.replace("_", "/")

    x2, y2 = addCell(pdf, tableX, tableY+cellHeight, 25,  cellHeight, callsign)
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 25, cellHeight, datetime.datetime.utcfromtimestamp(data["timestamp"]).strftime('%Y-%m-%d'))
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15, cellHeight, datetime.datetime.utcfromtimestamp(data["timestamp"]).strftime('%H:%M'))
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15,  cellHeight, data["band"])
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15,  cellHeight, data["mode"])
    x2, y2 = addCell(pdf, x2, tableY+cellHeight, 15,  cellHeight, data["rst_received"])

    

    pdf.set_xy(5, 67)
    pdf.set_font('myfont', size=7)
    pdf.set_char_spacing(9)
    pdf.cell(w=W-10, h=0, text=f".... --. ..--- ..... -.-. -.-. ...", border=0, ln=0, align="c")
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

    pdf.set_title("HG25CCS")


    fileDir = os.path.dirname(out_path)
    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    pdf.output(out_path)

if __name__ == "__main__":
    data = {'band': '2m', 'mode': 'SSB', 'timestamp': 1784065936, 'qth': 'jn87if', 'rst_sent': '59', 'rst_received': '59', 'local_operator': 'HA1NBS', 'upload_timestamp_utc': 1753472357, 'uploaded_filename': 'ha1nb_URHOB_MIX_144_MHz.edi', 'callsign': 'ha1mp'}
    generate_fpdf("./tmp/test_qsl.pdf", data)









