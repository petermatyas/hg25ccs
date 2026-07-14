
# source: https://www.arrl.org/international-call-sign-series
import math
import json


"                      111111111122222222222333333"
"             123456789012345678901234567890123456"
characters = "abcdefghijklmnopqrstuvwxyz0123456789"
#characters = "012345678"

l = [
["AA-AL","United States of America"],
["AM-AO","Spain"],
["AP-AS","Pakistan"],
["AT-AW","India"],
["AX-AX","Australia"],
["AY-AZ","Argentine Republic"],
["A2-A2","Botswana"],
["A3-A3","Tonga (Kingdom of)"],
["A4-A4","Oman (Sultanate of)"],
["A5-A5","Bhutan (Kingdom of)"],
["A6-A6","United Arab Emirates"],
["A7-A7","Qatar (State of)"],
["A8-A8","Liberia (Republic of)"],
["A9-A9","Bahrain (State of)"],
["BA-BZ","China (People's Republic of)"],
["CA-CE","Chile"],
["CF-CK","Canada"],
["CL-CM","Cuba"],
["CN-CN","Morocco (Kingdom of)"],
["CO-CO","Cuba"],
["CP-CP","Bolivia (Republic of)"],
["CQ-CU","Portugal"],
["CV-CX","Uruguay (Eastern Republic of)"],
["CY-CZ","Canada"],
["C2-C2","Nauru (Republic of)"],
["C3-C3","Andorra (Principality of)"],
["C4-C4","Cyprus (Republic of)"],
["C5-C5","Gambia (Republic of the)"],
["C6-C6","Bahamas (Commonwealth of the)"],
["C7-C7","World Meteorological Organization"],
["C8-C9","Mozambique (Republic of)"],
["DA-DR","Germany (Federal Republic of)"],
["DS-DT","Korea (Republic of)"],
["DU-DZ","Philippines (Republic of the)"],
["D2-D3","Angola (Republic of)"],
["D4-D4","Cape Verde (Republic of)"],
["D5-D5","Liberia (Republic of)"],
["D6-D6","Comoros (Islamic Federal Republic of the)"],
["D7-D9","Korea (Republic of)"],
["EA-EH","Spain"],
["EI-EJ","Ireland"],
["EK-EK","Armenia (Republic of)"],
["EL-EL","Liberia (Republic of)"],
["EM-EO","Ukraine"],
["EP-EQ","Iran (Islamic Republic of)"],
["ER-ER","Moldova (Republic of)"],
["ES-ES","Estonia (Republic of)"],
["ET-ET","Ethiopia (Federal Democratic Republic of)"],
["EU-EW","Belarus (Republic of)"],
["EX-EX","Kyrgyz Republic"],
["EY-EY","Tajikistan (Republic of)"],
["EZ-EZ","Turkmenistan"],
["E2-E2","Thailand"],
["E3-E3","Eritrea"],
["E4-E4","Palestinian Authority"],
["E5-E5","New Zealand - Cook Islands"],
["E6-E6","New Zealand - Niue"],
["E7-E7","Bosnia and Herzegovina (Republic of)"],
["F-F","France"],
["GA-GZ","United Kingdom of Great Britain and Northern Ireland"],
["HA-HA","Hungary (Republic of)"],
["HB-HB","Switzerland (Confederation of)"],
["HC-HD","Ecuador"],
["HE-HE","Switzerland (Confederation of)"],
["HF-HF","Poland (Republic of)"],
["HG-HG","Hungary (Republic of)"],
["HH-HH","Haiti (Republic of)"],
["HI-HI","Dominican Republic"],
["HJ-HK","Colombia (Republic of)"],
["HL-HL","Korea (Republic of)"],
["HM-HM","Democratic People's Republic of Korea"],
["HN-HN","Iraq (Republic of)"],
["HO-HP","Panama (Republic of)"],
["HQ-HR","Honduras (Republic of)"],
["HS-HS","Thailand"],
["HT-HT","Nicaragua"],
["HU-HU","El Salvador (Republic of)"],
["HV-HV","Vatican City State"],
["HW-HY","France"],
["HZ-HZ","Saudi Arabia (Kingdom of)"],
["H2-H2","Cyprus (Republic of)"],
["H3-H3","Panama (Republic of)"],
["H4-H4","Solomon Islands"],
["H6-H7","Nicaragua"],
["H8-H9","Panama (Republic of)"],
["IA-IZ","Italy"],
["JA-JS","Japan"],
["JT-JV","Mongolia"],
["JW-JX","Norway"],
["JY-JY","Jordan (Hashemite Kingdom of)"],
["JZ-JZ","Indonesia (Republic of)"],
["J2-J2","Djibouti (Republic of)"],
["J3-J3","Grenada"],
["J4-J4","Greece"],
["J5-J5","Guinea-Bissau (Republic of)"],
["J6-J6","Saint Lucia"],
["J7-J7","Dominica (Commonwealth of)"],
["J8-J8","Saint Vincent and the Grenadines"],
["KA-KZ","United States of America"],
["LA-LN","Norway"],
["LO-LW","Argentine Republic"],
["LX-LX","Luxembourg"],
["LY-LY","Lithuania (Republic of)"],
["LZ-LZ","Bulgaria (Republic of)"],
["L2-L9","Argentine Republic"],
["MA-MZ","United Kingdom of Great Britain and Northern Ireland"],
["NA-NZ","United States of America"],
["OA-OC","Peru"],
["OD-OD","Lebanon"],
["OE-OE","Austria"],
["OF-OJ","Finland"],
["OK-OL","Czech Republic"],
["OM-OM","Slovak Republic"],
["ON-OT","Belgium"],
["OU-OZ","Denmark"],
["PA-PI","Netherlands (Kingdom of the)"],
["PJ-PJ","Netherlands (Kingdom of the) - Netherlands Caribbean"],
["PK-PO","Indonesia (Republic of)"],
["PP-PY","Brazil (Federative Republic of)"],
["PZ-PZ","Suriname (Republic of)"],
["P2-P2","Papua New Guinea"],
["P3-P3","Cyprus (Republic of)"],
["P4-P4","Netherlands (Kingdom of the) - Aruba"],
["P5-P9","Democratic People's Republic of Korea"],
["RA-RZ","Russian Federation"],
["SA-SM","Sweden"],
["SN-SR","Poland (Republic of)"],
["SSA-SSM","Egypt (Arab Republic of)"],
["SSN-STZ","Sudan (Republic of the)"],
["SU-SU","Egypt (Arab Republic of)"],
["SV-SZ","Greece"],
["S2-S3","Bangladesh (People's Republic of)"],
["S5-S5","Slovenia (Republic of)"],
["S6-S6","Singapore (Republic of)"],
["S7-S7","Seychelles (Republic of)"],
["S8-S8","South Africa (Republic of)"],
["S9-S9","Sao Tome and Principe (Democratic Republic of)"],
["TA-TC","Turkey"],
["TD-TD","Guatemala (Republic of)"],
["TE-TE","Costa Rica"],
["TF-TF","Iceland"],
["TG-TG","Guatemala (Republic of)"],
["TH-TH","France"],
["TI-TI","Costa Rica"],
["TJ-TJ","Cameroon (Republic of)"],
["TK-TK","France"],
["TL-TL","Central African Republic"],
["TM-TM","France"],
["TN-TN","Congo (Republic of the)"],
["TO-TQ","France"],
["TR-TR","Gabonese Republic"],
["TS-TS","Tunisia"],
["TT-TT","Chad (Republic of)"],
["TU-TU","Côte d'Ivoire (Republic of)"],
["TV-TX","France"],
["TY-TY","Benin (Republic of)"],
["TZ-TZ","Mali (Republic of)"],
["T2-T2","Tuvalu"],
["T3-T3","Kiribati (Republic of)"],
["T4-T4","Cuba"],
["T5-T5","Somali Democratic Republic"],
["T6-T6","Afghanistan (Islamic State of)"],
["T7-T7","San Marino (Republic of)"],
["T8-T8","Palau (Republic of)"],
["UA-UI","Russian Federation"],
["UJ-UM","Uzbekistan (Republic of)"],
["UN-UQ","Kazakhstan (Republic of)"],
["UR-UZ","Ukraine"],
["VA-VG","Canada"],
["VH-VN","Australia"],
["VO-VO","Canada"],
["VP-VQ","United Kingdom of Great Britain and Northern Ireland"],
["VR-VR","China (People's Republic of) - Hong Kong"],
["VS-VS","United Kingdom of Great Britain and Northern Ireland"],
["VT-VW","India (Republic of)"],
["VX-VY","Canada"],
["VZ-VZ","Australia"],
["V2-V2","Antigua and Barbuda"],
["V3-V3","Belize"],
["V4-V4","Saint Kitts and Nevis"],
["V5-V5","Namibia (Republic of)"],
["V6-V6","Micronesia (Federated States of)"],
["V7-V7","Marshall Islands (Republic of the)"],
["V8-V8","Brunei Darussalam"],
["WA-WZ","United States of America"],
["XA-XI","Mexico"],
["XJ-XO","Canada"],
["XP-XP","Denmark"],
["XQ-XR","Chile"],
["XS-XS","China (People's Republic of)"],
["XT-XT","Burkina Faso"],
["XU-XU","Cambodia (Kingdom of)"],
["XV-XV","Viet Nam (Socialist Republic of)"],
["XW-XW","Lao People's Democratic Republic"],
["XX-XX","China (People's Republic of) - Macao"],
["XY-XZ","Myanmar (Union of)"],
["YA-YA","Afghanistan (Islamic State of)"],
["YB-YH","Indonesia (Republic of)"],
["YI-YI","Iraq (Republic of)"],
["YJ-YJ","Vanuatu (Republic of)"],
["YK-YK","Syrian Arab Republic"],
["YL-YL","Latvia (Republic of)"],
["YM-YM","Turkey"],
["YN-YN","Nicaragua"],
["YO-YR","Romania"],
["YS-YS","El Salvador (Republic of)"],
["YT-YU","Serbia (Republic of)"],
["YV-YY","Venezuela (Republic of)"],
["Y2-Y9","Germany (Federal Republic of)"],
["ZA-ZA","Albania (Republic of)"],
["ZB-ZJ","United Kingdom of Great Britain and Northern Ireland"],
["ZK-ZM","New Zealand"],
["ZN-ZO","United Kingdom of Great Britain and Northern Ireland"],
["ZP-ZP","Paraguay (Republic of)"],
["ZQ-ZQ","United Kingdom of Great Britain and Northern Ireland"],
["ZR-ZU","South Africa (Republic of)"],
["ZV-ZZ","Brazil (Federative Republic of)"],
["Z2-Z2","Zimbabwe (Republic of)"],
["Z3-Z3","North Macedonia (Republic of)"],
["Z6-Z6","Kosovo (Republic of)"],
["Z8-Z8","South Sudan (Republic of)"],
["3A-3A","Monaco (Principality of)"],
["3B-3B","Mauritius (Republic of)"],
["3C-3C","Equatorial Guinea (Republic of)"],
["3DA-3DM","Kingdom of Eswatini"],
["3DN-3DZ","Fiji (Republic of)"],
["3E-3F","Panama (Republic of)"],
["3G-3G","Chile"],
["3H-3U","China (People's Republic of)"],
["3V-3V","Tunisia"],
["3W-3W","Viet Nam (Socialist Republic of)"],
["3X-3X","Guinea (Republic of)"],
["3Y-3Y","Norway"],
["3Z-3Z","Poland (Republic of)"],
["4A-4C","Mexico"],
["4D-4I","Philippines (Republic of the)"],
["4J-4K","Azerbaijani Republic"],
["4L-4L","Georgia (Republic of)"],
["4M-4M","Venezuela (Republic of)"],
["4O-4O","Montenegro (Republic of)"],
["4P-4S","Sri Lanka (Democratic Socialist Republic of)"],
["4T-4T","Peru"],
["4U-4U","United Nations"],
["4V-4V","Haiti (Republic of)"],
["4W-4W","Democratic Republic of Timor-Leste   (WRC-03)"],
["4X-4X","Israel (State of)"],
["4Y-4Y","International Civil Aviation Organization"],
["4Z-4Z","Israel (State of)"],
["5A-5A","Libya (Socialist People's Libyan Arab Jamahiriya)"],
["5B-5B","Cyprus (Republic of)"],
["5C-5G","Morocco (Kingdom of)"],
["5H-5I","Tanzania (United Republic of)"],
["5J-5K","Colombia (Republic of)"],
["5L-5M","Liberia (Republic of)"],
["5N-5O","Nigeria (Federal Republic of)"],
["5P-5Q","Denmark"],
["5R-5S","Madagascar (Republic of)"],
["5T-5T","Mauritania (Islamic Republic of)"],
["5U-5U","Niger (Republic of the)"],
["5V-5V","Togolese Republic"],
["5W-5W","Samoa (Independent State of)"],
["5X-5X","Uganda (Republic of)"],
["5Y-5Z","Kenya (Republic of)"],
["6A-6B","Egypt (Arab Republic of)"],
["6C-6C","Syrian Arab Republic"],
["6D-6J","Mexico"],
["6K-6N","Korea (Republic of)"],
["6O-6O","Somali Democratic Republic"],
["6P-6S","Pakistan (Islamic Republic of)"],
["6T-6U","Sudan (Republic of the)"],
["6V-6W","Senegal (Republic of)"],
["6X-6X","Madagascar (Republic of)"],
["6Y-6Y","Jamaica"],
["6Z-6Z","Liberia (Republic of)"],
["7A-7I","Indonesia (Republic of)"],
["7J-7N","Japan"],
["7O-7O","Yemen (Republic of)"],
["7P-7P","Lesotho (Kingdom of)"],
["7Q-7Q","Malawi"],
["7R-7R","Algeria (People's Democratic Republic of)"],
["7S-7S","Sweden"],
["7T-7Y","Algeria (People's Democratic Republic of)"],
["7Z-7Z","Saudi Arabia (Kingdom of)"],
["8A-8I","Indonesia (Republic of)"],
["8J-8N","Japan"],
["8O-8O","Botswana (Republic of)"],
["8P-8P","Barbados"],
["8Q-8Q","Maldives (Republic of)"],
["8R-8R","Guyana"],
["8S-8S","Sweden"],
["8T-8Y","India (Republic of)"],
["8Z-8Z","Saudi Arabia (Kingdom of)"],
["9A-9A","Croatia (Republic of)"],
["9B-9D","Iran (Islamic Republic of)"],
["9E-9F","Ethiopia (Federal Democratic Republic of)"],
["9G-9G","Ghana"],
["9H-9H","Malta"],
["9I-9J","Zambia (Republic of)"],
["9K-9K","Kuwait (State of)"],
["9L-9L","Sierra Leone"],
["9M-9M","Malaysia"],
["9N-9N","Nepal"],
["9O-9T","Democratic Republic of the Congo"],
["9U-9U","Burundi (Republic of)"],
["9V-9V","Singapore (Republic of)"],
["9W-9W","Malaysia"],
["9X-9X","Rwandese Republic"],
["9Y-9Z","Trinidad and Tobago"],
]
 
 
l = [["9a-9a","test"]]


def charToNr(char):
    for idx, i in enumerate(characters):
        if i == char:
            return idx+1

def nrToChar(nr):
    return characters[nr-1]


def strToNr(inpStr:str):
    res = 0
    #str_orig = str

    for i in range(len(inpStr)):
        multiplier = pow(len(characters), len(inpStr)-1-i)
        #print("strToNr",i, "\t", str[i], "*", multiplier)                 
        res += charToNr(inpStr[i])*multiplier
    #print(str_orig, "-->", res)
    return res

def nrToStr(nr):
    res = ""
    nr_orig = nr
    if nr == 0:
        nrOfChars = 1
    elif nr == 1:
        nrOfChars = 1
    else:
        nrOfChars = math.ceil(math.log(nr)/math.log(len(characters)))
    #print("nrOfChars", nrOfChars)

    for _ in range(nrOfChars):   
        res = nrToChar(nr % len(characters)) + res 
        print("--", nr, "\t", nr % len(characters), res)
        nr = math.ceil(nr / len(characters))
        #print("- nr2:", nr)

    #print(nr_orig, "-->", res, nrOfChars)
    return res

def generatePrefixDb():
    db = dict()

    for i in l:
        fromStr = i[0].split("-")[0].lower()
        toStr   = i[0].split("-")[1].lower()
        country = i[1]
        #print(fromStr, toStr, country)

        for i in range(strToNr(fromStr), strToNr(toStr)+1, 1):
            prefix = nrToStr(i)
            print(i, nrToStr(i))
            db[prefix] = country.replace(" (Republic of)", "")


    #with open('prefixDb.json', 'w') as f:
    #    json.dump(db, f)



def getCountry(callsign):
    with open('prefixDb.json') as f:
        d = json.load(f)

    for i in d:
        #print(i)
        if callsign.lower().startswith(i):
            return d[i]
    return None




if __name__ == "__main__":

    #print(getCountry("HA7TM"))
    #generatePrefixDb()

    #print(nrToStr(36))
    #print(nrToStr(37))
    #print(nrToStr(1296))
    print(nrToStr(1297))
    generatePrefixDb()