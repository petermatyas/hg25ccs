import re
import datetime


def freqToBand(freq):
    # frequency [Hz]
    freq = int(freq)

    if 1800 <= freq and freq <= 2000:
        return "160m"
    elif 3500 <= freq and freq <= 3800:
        return "80m"
    elif 5300 <= freq and freq <= 5400: 
        return "60m"
    elif 7000 <= freq and freq <= 7200: 
        return "40m"
    elif 10100 <= freq and freq <= 10150:
        return "30m"
    elif 14000 <= freq and freq <= 14350:
        return "20m"
    elif 18068 <= freq and freq <= 18268:
        return "17m"
    elif 21000 <= freq and freq <= 21450:
        return "15m"
    elif 24890 <= freq and freq <= 24990:
        return "12m"
    elif 28000 <= freq and freq <= 29700:
        return "10m"
    elif 50000 <= freq and freq <= 52000:
        return "6m"
    elif 70000 <= freq and freq <= 70500:
        return "4m"
    elif 144000 <= freq and freq <= 146000:
        return "2m"
    elif 420000 <= freq and freq <= 450000:
        return "70cm"
    elif 902000 <= freq and freq <= 928000:
        return "33cm"
    elif 1240000 <= freq and freq <= 1300000:
        return "23cm"
    elif 2300000 <= freq and freq <= 2450000:
        return "13cm"
    elif 3300000 <= freq and freq <= 3500000:
        return "9cm"

    else:
        return "error"

def clearCallsign(callsign):

    if callsign.upper().endswith("/P"):
        callsign = callsign[:-2]
    elif callsign.upper().endswith("/M"):
        callsign = callsign[:-2]
    elif callsign.upper().endswith("/MM"):
        callsign = callsign[:-3]
    elif callsign.upper().endswith("/QRP"):
        callsign = callsign[:-4]

    return callsign.upper()



def process_callibro(filePath, uploadedFileName, uploadTimestamp):
    """
    https://wwrof.org/cabrillo/cabrillo-v3-header/
    """
    with open(filePath, "r", encoding="ISO-8859-1") as file:
        content = file.read()

    #callsign = re.findall("CALLSIGN: (.+)", content)[0]
    #print(callsign)

    modeDict = {"CW":"CW", "PH":"SSB", "FM":"FM", "RY":"RTTY", "DG":"DG"}
    '''bandDict = {"1800":"160m", "3500":"80m", "7000":"40m", "14000":"20m", "21000":"15m", "28000":"10m", "50":"6m", 
                "70":"4m", "144":"2m", "222":"?m", "432":"70cm", "902":"33cm", "1.2G":"23cm", "2.3G":"13cm", 
                "3.4G":"?cm", "5.7G":"?cm", "10G":"?cm", "24G":"?cm", "47G":"?cm", "75G":"?cm", "122G":"?cm", 
                "134G":"?cm", "241G":"?cm", "LIGHT":"??"}'''
    
    try:
        operator_name = re.findall("NAME: (.+)", content)[0]
    except:
        operator_name = "error"
    try:
        operator_callsign = re.findall("CALLSIGN: (.+)", content)[0]
    except:
        operator_callsign = "error"


    logs = re.findall("QSO:.+|X-QSO:.+", content)
    res = list()
    for i in logs:
        i = i.replace(":", " ")
        line = i.split()
        #line = re.split(':| ', i)
        try:
            freq = line[1]
            if freq[-1].lower() == "g":
                freq = int(freq)*1000000
            elif int(freq) < 1000:
                freq = int(freq)*1000
            else:
                freq = int(freq)*1

            band = freqToBand(freq)

        except:
            band = "error"
        
        try:
            mode = line[2]
        except:
            mode = "error"
        
        try:
            callsign = line[8]
            callsign = clearCallsign(callsign)
        except:
            callsign = "error"

        try:
            #print("-----------", line)
            date = line[3]
            time = line[4]
            dt = datetime.datetime.strptime(date + time, "%Y-%m-%d%H%M")
            log_utc_ts = datetime.datetime.timestamp(dt)
        except:
            log_utc_ts = "[ERROR] date:"+date+"_time:"+time

        try:
            qth = "none"
        except:
            qth = "error"

        try:
            rst_sent = line[6]
        except:
            rst_sent = "error"

        try:
            rst_rec = line[9]
        except:
            rst_rec = "error"

        if operator_name != "error":
            operator = operator_name
        elif operator_callsign != "error":
            operator = operator_callsign
        else:
            operator = "error"



        res.append({"callsign":callsign.upper(), 
                    "band":band, 
                    "mode":modeDict[mode],
                    "qth":qth.lower(),
                    "log_utc_timestamp":log_utc_ts, 
                    "uploaded_file_name":uploadedFileName, 
                    "upload_timestamp_utc":uploadTimestamp,
                    "rst_sent":rst_sent,
                    "rst_rec":rst_rec,
                    "local_operator":operator})
        #print(callsign, band, modeDict[mode])

    return res

def process_edi(filePath, uploadedFileName, uploadTimestamp):
    """
    https://www.ok2kkw.com/ediformat.htm
    """
    with open(filePath, "r", encoding="ISO-8859-1") as file:
        content = file.read()

    bandDict = {"50 MHz": "6m", "70 MHz":"4m", "144 MHz": "2m", "432 MHz":"70cm", "1,3 GHz":"23cm"}
    modeDict = {"0":"??", "1":"SSB", "2":"CW", "3":"CW", "4":"SSB", "5":"AM", "6":"FM", "7":"RTTY", "8":"SSTV", "9":"ATV"}

    try:
        operator_mopel = re.findall("MOpe1=(.+)", content)[0]
    except:
        operator_mopel = "error"
    try:
        operator_pcall = re.findall("PCall=(.+)", content)[0]
    except:
        operator_pcall = "error"
    try:
        operator_rcall = re.findall("RCall=(.+)", content)[0]
    except:
        operator_rcall = "error"


    band = re.findall("PBand=(.+)", content)[0]
    if band in bandDict:
        band = bandDict[band]
    else:
        band = "error_"+str(band)

    logs = re.findall(".+;.+;.+;.+", content)
    
    res = list()
    for i in logs:
        #print("logline: ", i)
        try:
            callsign = i.split(";")[2].upper()    
            callsign = clearCallsign(callsign)
        except:
            callsign = "error"
        
        try:
            modeCode = i.split(";")[3]
            mode = modeDict[modeCode].upper()
        except:
            mode = "error"
        
        try:
            date = i.split(";")[0]
            time = i.split(";")[1]
            dt = datetime.datetime.strptime(date + time, "%y%m%d%H%M")
            log_utc_ts = datetime.datetime.timestamp(dt)                   
        except:
            log_utc_ts = "[ERROR] date:"+date+"_time:"+time 

        try:
            qth = i.split(";")[9]
        except:
            qth = "none"

        try:
            rst_sent = i.split(";")[6]
        except:
            rst_sent = "error"

        try:
            rst_rec = i.split(";")[4]
        except:
            rst_rec = "error"

        if operator_mopel != "error":
            operator = operator_mopel
        elif operator_pcall != "error":
            operator = operator_pcall
        elif operator_rcall != "error":
            operator = operator_rcall
        else:
            operator = "error"


        res.append({"callsign":callsign.upper(), 
                    "band":band, 
                    "mode":mode, 
                    "qth":qth.lower(),
                    "log_utc_timestamp":log_utc_ts,
                    "uploaded_file_name":uploadedFileName,
                    "upload_timestamp_utc": uploadTimestamp,
                    "rst_sent":rst_sent,
                    "rst_rec":rst_rec,
                    "local_operator":operator
                    })
        #print(callsign, band, mode)

    return res

def process_adif(filePath, uploadedFileName, uploadTimestamp):
    """
    https://www.adif.org/100/adif_100.htm
    """

    modeDict = {"mfsk":"ft4"}

    with open(filePath, "r", encoding="ISO-8859-1") as file:
        content = file.read()

    try:
        local_operator_name = re.findall("name:* *(ha[a-z0-9/]+)", content.lower())[0]
    except:
        local_operator_name = "error"

    print("local_operator_name", local_operator_name)
    logs = re.findall("<.+<eor>", content.lower())

    res = list()
    for i in logs:
        #print("adif: ", i)
        try:
            callsign = re.findall("<call:([0-9]+)>([a-zA-Z0-9/]+)", i.lower())[0][1]
            if "/" in callsign:
                callsign = callsign.replace("/", "_") 
                callsign = clearCallsign(callsign)
        except:
            callsign = "error"
        
        try:
            if "band" in i.lower():
                band = re.findall("<band:([0-9]+>)([a-zA-Z0-9]+)", i.lower())[0][1]
            elif "freq" in i.lower():
                freq = re.findall("<freq:([0-9]+>)([0-9]+.?[0-9]+)", i.lower())[0][1]
                band = freqToBand(float(freq) * 1000)
            else:
                band = "error"
        except:
            band = "error"
        
        try:
            mode = re.findall("<mode:([0-9]+>)([a-zA-Z0-9]+)", i.lower())[0][1]
            if mode.lower() in modeDict:
                mode = modeDict[mode.lower()]
        except:
            log_utc_ts = "[ERROR] date:"+date+"_time:"+time

        try:
            date = re.findall("<qso_date:([0-9]+>)([a-zA-Z0-9]+)", i.lower())[0][1]
            time = re.findall("<time_on:([0-9]+>)([a-zA-Z0-9]+)", i.lower())[0][1]
            dt = datetime.datetime.strptime(date + time, "%Y%m%d%H%M%S")
            log_utc_ts = datetime.datetime.timestamp(dt) 
        except:
            pass

        try:
            qth = re.findall("<gridsquare:([0-9]+>)([a-zA-Z0-9]+)", i.lower())[0][1]
        except:
            qth = "none"

        try:
            rst_sent_res = re.findall("rst_sent:([0-9]+>)([0-9]+)|rst_sent:([0-9]+>)([+-]?[0-9]+)", i.lower())[0]
            if rst_sent_res[1] != "":
                rst_sent = rst_sent_res[1]
            elif rst_sent_res[3] != "":
                rst_sent = rst_sent_res[3]
            else:
                rst_sent = "error2"
        except:
            rst_sent = "error"

        try:
            rst_rec_res = re.findall("rst_rcvd:([0-9]+>)([0-9]+)|rst_rcvd:([0-9]+>)([+-]?[0-9]+)", i.lower())[0]
            if rst_rec_res[1] != "":
                rst_rec = rst_rec_res[1]
            elif rst_rec_res[3] != "":
                rst_rec = rst_rec_res[3]
            else:
                rst_rec = "error2"
        except:
            rst_rec = "error"

        #try:
        #    local_operator_station = re.findall("station_callsign:([0-9]+>)([a-z0-9]+)", i.lower())[0][1]
        #    print("local_operator_station", local_operator_station)
        #except:
        #    local_operator_station = "error"

        try:
            local_operator_operator = re.findall("operator:([0-9]+>)([a-z0-9/]+)", i.lower())[0][1]
            print("local_operator_operator", local_operator_operator)
        except:
            local_operator_operator = "error"
        print("local_operator_name", local_operator_name)
        
        if local_operator_name != "error":
            local_operator = local_operator_name
        #elif local_operator_station != "error":
        #    local_operator = local_operator_station
        elif local_operator_operator != "error":
            local_operator = local_operator_operator
        else:
            local_operator = "error"


        res.append({"callsign":callsign.upper(), 
                    "band":band, 
                    "mode":mode.upper(), 
                    "qth":qth.lower(),
                    "log_utc_timestamp":log_utc_ts, 
                    "uploaded_file_name":uploadedFileName, 
                    "upload_timestamp_utc":uploadTimestamp,
                    "rst_rec":rst_rec,
                    "rst_sent":rst_sent,
                    "local_operator":local_operator
                    })
        #print(callsign, band, mode)
    
    return res


def process(filePath, uploadedFileName, uploadTimestamp):
    extension = filePath.split(".")[-1]

    if extension.lower() in ["edi"]:
        logLines = process_edi(filePath, uploadedFileName, uploadTimestamp)
    elif extension.lower() in ["adi", "adif"]:
        logLines = process_adif(filePath, uploadedFileName, uploadTimestamp)
    elif extension.lower() in ["cbr", "log"]:
        logLines = process_callibro(filePath, uploadedFileName, uploadTimestamp)
    else:
        return "file extension error"

    return logLines


if __name__ == "__main__":
    #for i in process_callibro("./logs/HG24SA.cbr", "HG24SA.cbr", 1234567):
    #    print(i)
    #for i in process_adif("./test/wsjtx_log_04_18-ADI.adi", "wsjtx_log_04_18-ADI.adi", 1234567):
    #    print(i)
    #for i in process_edi("./test/HA1MP_01.edi", "HA1MP_01.edi", 12345678):
    #    print(i)
    #for i in process_adif("./Test logok/MixW2_1IN_1DLI.adi", "MixW2_1IN_1DLI.adi", 1234567):
    #    print(i)
    

    path = "/home/ha1mp/Projektek/hg1ccs/backend/Test_logok/00_test.CBR"
    for i in process(path, "00", 0):
        print(i)
        #pass
    
    """
    print(clearCallsign("ha/qrp1mp"))
    print(clearCallsign("ha1mp/mm"))
    print(clearCallsign("ha1mp/p"))
    """


