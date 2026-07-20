from typing import Union
#from typing import Annotated

from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


import uvicorn

import time
from datetime import datetime, timezone
import pytz
import os
import threading
from zipfile import ZipFile

from dotenv import load_dotenv

import handle_log
import handle_db
import diploma
import qsl
import country
import auth

baseDir = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


activeBandList = list()
activeBandListLog = list()
baseDir = os.path.dirname(os.path.realpath(__file__))

bands     = ["70cm", "2m", "4m", "6m", "10m", "12m", "15m", "17m", "20m", "30m", "40m", "60m", "80m", "160m"]
modes     = ["CW", "SSB", "FM", "DIGI"]
operators = ["HA1LS", "HA1MP", "HA1NB", "HA1NBS", "HA1WD", "HA1YA", "HA1WA"]

modes.sort()
operators.sort()

if not os.path.exists(os.path.join(baseDir, "qsls")):
    os.makedirs(os.path.join(baseDir, "qsls"))

@app.get("/api/v1")
def read_root():
    #return {"Hello": "World"}
    return RedirectResponse(url='/docs')


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/v1/login", tags=["auth"])
def login(creds: LoginRequest):
    if not auth.verify_credentials(creds.username, creds.password):
        raise HTTPException(status_code=401, detail="Hibás felhasználónév vagy jelszó")
    return {"token": auth.create_token(creds.username), "username": creds.username}


@app.get("/api/v1/me", tags=["auth"])
def me(username: str = Depends(auth.require_auth)):
    """A token érvényességének ellenőrzése; visszaadja a felhasználónevet."""
    return {"username": username}


def preGenerateDiplomas(callsignList):
    for callsign in callsignList:
        print("diploma generation", callsign)
        diploma.generate(callsign, "en")



@app.post("/api/v1/logs", tags=["log"], dependencies=[Depends(auth.require_auth)])
async def upload_log_file(file: UploadFile):

    ts = int(time.time())
    
    extension = file.filename.split(".")[-1]
    name = file.filename.replace("."+extension, "")

    logDir = os.path.join(baseDir, "logs")
    fileLocation = os.path.join(logDir, f"{name}_{ts}.{extension}")
    #print("fileLocation: ", fileLocation)
    #fileType = file.filename
    #print("fileType: ", fileType)

    newFile = await file.read()
    with open(fileLocation, "wb+") as file_object:
        #file_object.write(file.file.read())
        file_object.write(newFile)

    uploadTs = int(time.time())
    
    logLines = handle_log.process(fileLocation, name+"."+extension, uploadTs)
    """#print("----------------------------", extension.lower())
    if extension.lower() in ["edi"]:
        logLines = handle_log.process_edi(fileLocation, name+"."+extension, uploadTs)
    elif extension.lower() in ["adi", "adif"]:
        #print("----------------------------")
        logLines = handle_log.process_adif(fileLocation, name+"."+extension, uploadTs)
    elif extension.lower() in ["cbr", "log"]:
        logLines = handle_log.process_callibro(fileLocation, name+"."+extension, uploadTs)
    else:
        return "file extension error"
    """
    #callsignList = [i["callsign"] for i in logLines]
    #print(callsignList)
    """x = threading.Thread(target=preGenerateDiplomas, args=(callsignList,))
    x.start()
    #x.join()"""
    #print(logLines)
    handle_db.addLogs(logLines)
    handle_db.readLogs()




    return {"info": f"file '{file.filename}' saved at '{fileLocation}'"}

@app.get("/api/v1/log_uploads", tags=["log"], dependencies=[Depends(auth.require_auth)])
def getUploadTs():
    return handle_db.getUploads()

"""@app.get("/last_logs")
def getLogs():
    res = list()

    logQuery = handle_db.readLogs()
    if len(logQuery) == 0:
        return []
    for i in logQuery:
        res.append({"callsign":i.callsign, 
                    "band":i.band, 
                    "mode":i.mode, 
                    "log_timestamp":i.log_timestamp_utc, 
                    "upload_timestamp":i.upload_timestamp_utc})
    return res"""

@app.get("/api/v1/logs", tags=["log"], dependencies=[Depends(auth.require_auth)])
def logs(ts, filename):
    res = handle_db.queryByUpload(ts, filename)

    return [{"callsign":i.callsign,
             "band":i.band,
             "mode":i.mode,
             "local_operator":i.local_operator,
             "log_timestamp_utc":i.log_timestamp_utc} for i in res]

@app.get("/api/v1/logs_by_callsign", tags=["log"])
def logsByCallsign(callsign):
    
    qsos = handle_db.query(callsign)
    downloadedQslTs = handle_db.getDownloadedQslTimestamps(callsign)
    for qso in qsos:
        qso["qsl_downloaded"] = int(qso["timestamp"]) in downloadedQslTs
    return {
        "diploma_downloaded": handle_db.isDiplomaDownloaded(callsign),
        "qsos": qsos,
    }


@app.delete("/api/v1/logs", tags=["log"], dependencies=[Depends(auth.require_auth)])
def removeLogs(ts, filename):
    handle_db.removeLogs(ts, filename)
    return ""

def dropDuplites(k):
    k_cleaned = []
    for ele in k:
        if set(ele) not in [set(x) for x in k_cleaned]:
            k_cleaned.append(ele)
    return k_cleaned



class ActiveBandMode(BaseModel):
    callsign: str
    band: str
    mode: str

@app.post("/api/v1/active_band", tags=["active_band"], dependencies=[Depends(auth.require_auth)])
def set_active_band(band_mode: ActiveBandMode):
    global activeBandList
    callsign = band_mode.callsign
    band = band_mode.band
    mode = band_mode.mode

    if handle_db.sbActivatedBand(callsign):
        return {"error":"Már aktiváltál sávot"}
    elif handle_db.isBandActive(callsign, band, mode):
        return {"error":"Ezen a sávon és módon már forgalmaz valaki"}
    else:
        handle_db.activateBand(callsign, band, mode)
        return {"error":None}
    return ""

@app.get("/api/v1/active_band", tags=["active_band"], dependencies=[Depends(auth.require_auth)])
def get_active_bands():
    #return activeBandList
    return handle_db.getActiveBands()

@app.delete("/api/v1/active_band", tags=["active_band"], dependencies=[Depends(auth.require_auth)])
def delete_active_band(callsign:str, band:str, mode:str):
    handle_db.deactivateBand(callsign, band, mode)
    '''for idx, i in enumerate(activeBandList):
        if i["callsign"] == callsign and i["band"] == band and i["mode"] == mode:
            activeBandList.pop(idx)
            activeBandListLog.append({"ts":int(time.time()), 
                                      "datetime":datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
                                      "action":"deactivate", 
                                      "callsign":callsign, 
                                      "band":band, 
                                      "mode":mode})'''
    return ""

@app.get("/api/v1/active_band_log", tags=["active_band"], dependencies=[Depends(auth.require_auth)])
def get_active_band_log():
    #return activeBandListLog
    return handle_db.getActiveBandsHistory()

@app.get("/api/v1/bands", tags=["band"])
def get_bands():   
    return bands

@app.post("/api/v1/band", tags=["band"], dependencies=[Depends(auth.require_auth)])
def add_band(newBand:str):
    bands.append(newBand)
    
@app.get("/api/v1/modes", tags=["mode"])
def get_modes():   
    return modes

@app.post("/api/v1/mode", tags=["mode"], dependencies=[Depends(auth.require_auth)])
def add_mode(newMode:str):
    modes.append(newMode)
    modes.sort()

@app.get("/api/v1/operators", tags=["operator"])
def get_operators():   
    return operators

@app.post("/api/v1/operator", tags=["operator"], dependencies=[Depends(auth.require_auth)])
def add_operator(newOperator:str):
    operators.append(newOperator)
    operators.sort()

@app.get("/api/v1/generate_diploma", tags=["diploma"])
def generate_diploma(callsign, lang="en"):    
    #print("---------- generate diploma ---------------")
    #handle_db.diplomaQslDownload(callsign, "generateDiploma")
    qsos = handle_db.query(callsign)
    print(qsos)
    qsos_unique = list(set([(i["band"], i["mode"]) for i in qsos]))
    valid_qsos_nr = len(qsos_unique)

    print("érvényes qso-k:", qsos_unique, valid_qsos_nr < 3)

    if valid_qsos_nr >= 3 or callsign.lower() in ["Leon", "Ármin"]:
        #diplomaPath = f"./diplomas/diploma_{callsign.lower()}.pdf"
        lang = "en"
        callsign = callsign.replace("/", "_")
        diplomaPath = os.path.join(baseDir, "diplomas", f"diploma_{callsign.lower()}_{lang}.pdf")
        print("diplomaPath: ", diplomaPath)

        if not os.path.exists(diplomaPath):
            print("no diploma, generating...")
            diploma.generate_fpdf(callsign, diplomaPath, "en")

        return {"deserve": True, 
                "path": diplomaPath,
                "qso": qsos,
                "nr_of_valid_qso": valid_qsos_nr,
                #"result_text": resultText,
                #"status":status
                }
    
    else:
        return {"deserve":False,
                "path":None,
                "qso":qsos,
                "nr_of_valid_qso": valid_qsos_nr,
                #"result_text":resultText,
                }

@app.get("/api/v1/download_diploma", tags=["diploma"])
def download_diploma(callsign, lang="en"):
    if "/" in callsign:
        callsign = callsign.replace("/", "_")
    diplomaPath = os.path.join(baseDir, "diplomas", f"diploma_{callsign.lower()}_{lang}.pdf")
    if os.path.exists(diplomaPath):
        handle_db.diplomaDownload(callsign)
        return FileResponse(diplomaPath, media_type='application/octet-stream',filename=f"HG24CCS.pdf")
    else:
        return {"error":"not exists"}


@app.get("/api/v1/downloaded_diplomas", tags=["diploma"])
def downloaded_diplomas():
    return handle_db.getDownloadedDiplomas()


@app.get("/api/v1/generate_qsl", tags=["qsl"])
def generate_qsl(callsign, lang="en"):  
    #print("-------- generate qsl ------------")
    #handle_db.diplomaQslDownload(callsign, "generateQsl")
    
    qsos = handle_db.query(callsign)

    resList = list()

    if not os.path.exists(os.path.join(baseDir, "qsls")):
        os.makedirs(os.path.join(baseDir, "qsls"))
    for idx, qso in enumerate(qsos):

        callsign = callsign.replace("/", "_")
        qslPath = os.path.join(baseDir, "qsls", f'qsl_{callsign}_{qso["timestamp"]}.pdf')
        if not os.path.exists(qslPath):
            qso["callsign"] = callsign
            qsl.generate_fpdf(qslPath, qso)  
        resList.append({"name":f"{idx+1}.pdf","path":qslPath})

    #print(resList)
    return resList

@app.get("/api/v1/generate_all_qsl", tags=["qsl"])
def generate_all_qsl():
    for callsign in handle_db.getAllParticipant():
        print(callsign)
        generate_qsl(callsign)
    

@app.get("/api/v1/download_qsl", tags=["qsl"])
def downloaded_qsl(callsign, timestamp, fileNr):
    #handle_db.diplomaQslDownload(callsign, "downloadQsl")

    if "/" in callsign:
        callsign = callsign.replace("/", "_")
    qslPath = os.path.join(baseDir, "qsls", f'qsl_{callsign}_{timestamp}.pdf')
    if os.path.exists(qslPath):
        handle_db.qslDownload(callsign, timestamp)
        return FileResponse(qslPath, media_type='application/octet-stream',filename=f"{fileNr}.pdf")
    else:
        return {"error":"not exists"}

@app.get("/api/v1/statistics", tags=["statistics"])
def statistics():

    downloadedDiplomas_nr = len(list(set([i[1] for i in handle_db.getDownloadedDiplomas()])))

    valid_qso_1 = list()
    valid_qso_2 = list()
    valid_qso_3_or_more = list()
    modeBandTable = dict()


    bands_ext = bands.copy()
    bands_ext.append("error")
    bands_ext.append("other")
    modes_ext = modes.copy()
    modes_ext.append("error")
    modes_ext.append("other")

    for mode in modes_ext:
        modeBandTable[mode] = {}
        for band in bands_ext:
            modeBandTable[mode][band] = 0

    nrOfQsos = 0
    countryCounts = {}
    participants = handle_db.getAllParticipant()

    for callsign in participants:
        logs = handle_db.query(callsign)
        nrOfQsos += len(logs)

        c = country.getCountry(callsign) or "Ismeretlen"
        countryCounts[c] = countryCounts.get(c, 0) + len(logs)

        aa = [(i["band"], i["mode"]) for i in logs]
        for a in aa:
            #print("--", a)
            band = a[0]
            if not band in bands:
                band = "other"
            mode = a[1]
            if not mode in modes:
                if mode.lower() in ["ft4", "ft8"]:
                    mode = "DIGI"
                else:
                    mode = "other"
            modeBandTable[mode][band] += 1 


        aa = list(set(aa))
        if len(aa) == 1:
            valid_qso_1.append(callsign)
        elif len(aa) == 2:
            valid_qso_2.append(callsign)
        else:
            valid_qso_3_or_more.append(callsign)


    countriesSorted = sorted(countryCounts.items(), key=lambda kv: kv[1], reverse=True)
    countryStat = [{"country": k, "count": v} for k, v in countriesSorted]

    stat = {
        "nr_of_qso": nrOfQsos,
            "participanst_nr": len(participants),
            "modeBand": modeBandTable,
            "1validQso": valid_qso_1,
            "2validQso": valid_qso_2,
            "validDiploma": valid_qso_3_or_more,
            "downlodedDiplomaNr": downloadedDiplomas_nr,
            "countries": countryStat
            }

    return stat


@app.get("/api/v1/download_db", tags=["debug"], dependencies=[Depends(auth.require_auth)])
def downloadDb():
    #baseDir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(baseDir, "database", "logs.sqlite3")

    dateString = datetime.now().strftime("%Y%m%d%H%M%S")
    fileName = f"logs_{dateString}.sqlite3"

    return FileResponse(path, media_type='application/octet-stream',filename=fileName)


@app.get("/api/v1/download_logs", tags=["debug"], dependencies=[Depends(auth.require_auth)])
def downloadLogs():
    #baseDir = os.path.dirname(os.path.abspath(__file__))
    inputPath = os.path.join(baseDir, "logs")

    dateString = datetime.now().strftime("%Y%m%d%H%M%S")
    """
    TODO remove all zipfile
    """

    outFileName = f"logs_{dateString}.zip"
    outFilePath = os.path.join(outFileName)

    with ZipFile(outFilePath,'w') as zip:
        # writing each file one by one
        for file in os.listdir(inputPath):
            #print(file)
            zip.write(os.path.join(inputPath, file))

    return FileResponse(outFilePath, media_type='application/octet-stream',filename=outFileName)

@app.delete("/api/v1/remove_diplomas", tags=["debug"], dependencies=[Depends(auth.require_auth)])
def removeDiplomas():
    path = os.path.join(baseDir, "diplomas")

    fileNames = os.listdir(path)
    for fileName in fileNames:
        os.remove(os.path.join(path, fileName))
    
    return {"removed": fileNames}

@app.delete("/api/v1/remove_qsls", tags=["debug"], dependencies=[Depends(auth.require_auth)])
def removeQsls():
    path = os.path.join(baseDir, "qsls")

    fileNames = os.listdir(path)
    for fileName in fileNames:
        os.remove(os.path.join(path, fileName))
    
    return {"removed": fileNames}

@app.post("/api/v1/upload_file", tags=["debug"], dependencies=[Depends(auth.require_auth)])
async def upload_file(folder:str, file: UploadFile):

    fileLocation = os.path.join(baseDir, folder, file.filename)

    newFile = await file.read()
    with open(fileLocation, "wb+") as file_object:
        #file_object.write(file.file.read())
        file_object.write(newFile)

    return {"path": fileLocation}



if __name__ == "__main__":
    #uvicorn.run(app, host="0.0.0.0", port=8800, log_level="info")
    #statistics()
    generate_diploma("ha5l", lang="en")

