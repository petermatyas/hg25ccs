from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import select, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timezone
import pytz
import os


baseDir = os.path.dirname(os.path.realpath(__file__))
databaseDir = os.path.join(baseDir, "database")
databaseName = "logs.sqlite3"

databasePath = os.path.join(databaseDir, databaseName)


Base = declarative_base()

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    callsign = Column(String)
    band = Column(String)
    mode = Column(String)
    qth = Column(String)
    log_timestamp_utc = Column(Integer)
    upload_timestamp_utc = Column(Integer)
    uploaded_filename = Column(String)
    rst_sent = Column(String)
    rst_rec = Column(String)
    local_operator = Column(String)
    error = Column(String)

class ActiveBand(Base):
    __tablename__ = 'activeBand'
    id = Column(Integer, primary_key=True)
    callsign = Column(String)
    mode = Column(String)
    band = Column(String)
    start_timestamp_utc = Column(Integer)
    end_timestamp_utc = Column(Integer)

class DiplomaDownload(Base):
    __tablename__ = 'diplomaDownload'
    id = Column(Integer, primary_key=True)
    callsign = Column(String)
    timestamp_utc = Column(Integer)



if not os.path.exists(databaseDir):
    os.makedirs(databaseDir)

if not os.path.exists(databasePath):
    print("database not exists")
    import sqlite3
    conn = sqlite3.connect(databasePath)
    conn.close()
    print("database created")


engine = create_engine('sqlite:///'+databasePath, echo=False)
Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()


def getCurrentUtcTs():
    mytz = pytz.timezone('Europe/Budapest') 
    dt = datetime.now()
    timestamp_utc = mytz.normalize(mytz.localize(dt, is_dst=True)).timestamp()
    return int(timestamp_utc)


def addLogs(logList:list):
    for log in logList:
        def getValue(key, noValue):
            if key in log:
                return log[key]
            else:
                noValue

        callsign = getValue("callsign", "missing")
        mode = getValue("mode", "missing")
        band = getValue("band", "missing")
        log_timestamp_utc = getValue("log_utc_timestamp", 0) 
        qth = getValue("qth", "missing")
        upload_timestamp_utc = getValue("upload_timestamp_utc", 0) 
        uploaded_filename = getValue("uploaded_file_name", "filename")
        rst_sent = getValue("rst_sent", "missing")
        rst_rec = getValue("rst_rec", "missing")
        local_operator = getValue("local_operator", "missing")
        error = getValue("error", "no_error")
        
        queryObj = session.query(Log).where(Log.callsign == log["callsign"], 
                                            Log.band == log["band"], 
                                            Log.mode == log["mode"], 
                                            Log.qth == log["qth"],
                                            Log.rst_sent == log["rst_sent"],
                                            Log.rst_rec == log["rst_rec"],
                                            Log.log_timestamp_utc == log["log_utc_timestamp"],
                                            Log.local_operator == log["local_operator"]
                                            )
        if queryObj.first() == None:
            l = Log(
                callsign = callsign, 
                band = band,
                mode = mode,
                qth = qth,
                rst_sent = rst_sent,
                rst_rec = rst_rec,
                log_timestamp_utc = log_timestamp_utc,        
                upload_timestamp_utc = upload_timestamp_utc,
                uploaded_filename = uploaded_filename,
                local_operator = local_operator,
                error = error)
            session.add(l)

    session.commit()    

def readLogs():
    return session.query(Log).all()

def removeLogs(uploadTimestamp, filename):
    session.query(Log).where(Log.upload_timestamp_utc==uploadTimestamp and Log.uploaded_filename==filename).delete()
    session.commit() 

def query(callsign):
    #def query(callsign, startTs=None, stopTs=None):
    """tz = pytz.timezone("Europe/Budapest")
    if startTs == None:
        dt_start = datetime(2025, 1, 1, 0, 0, tzinfo=tz)
        startTs = int(dt_start.replace(tzinfo=timezone.utc).timestamp())
    if stopTs == None:
        dt_stop = datetime(2026, 1, 1, 0, 0, tzinfo=tz)
        stopTs = int(dt_stop.replace(tzinfo=timezone.utc).timestamp())"""

    #q = session.query(Log).where(Log.callsign==callsign.upper()).where(Log.log_timestamp_utc >= startTs).where(Log.log_timestamp_utc <= stopTs)
    q = session.query(Log).where(Log.callsign==callsign.upper())
    
    temp = list()
    for i in q:
        #print("7====", i.callsign, i.band, i.mode)
        #temp.append([i.band, i.mode, i.log_timestamp_utc])
        temp.append({"band":i.band, "mode":i.mode, "timestamp":i.log_timestamp_utc, "qth":i.qth, "rst_sent":i.rst_sent, "rst_received":i.rst_rec, 
                     "local_operator":i.local_operator, "upload_timestamp_utc": i.upload_timestamp_utc, "uploaded_filename":i.uploaded_filename})
    return temp

def queryByUpload(uploadTimestamp, filename):
    q = session.query(Log).where(Log.upload_timestamp_utc==uploadTimestamp and Log.uploaded_filename==filename)
    return q
    #return [{"band":i.band} for i in q]

def getUploads():
    stmt = select(Log.upload_timestamp_utc, Log.uploaded_filename).distinct().order_by(Log.upload_timestamp_utc.desc())
    res = session.execute(stmt)
    return [[i.upload_timestamp_utc, i.uploaded_filename] for i in res]

"""def getNrOfQsos():
    q = session.query(Log.callsign).count()
    return q"""

def getAllParticipant():
    q = session.query(Log.callsign).group_by(Log.callsign).all()
    """res = list()
    for i in q:
        res.append(i[0])
    return res"""
    return [i[0] for i in q]

"""def getAllParticipantOccurance():
    q = session.query(Log.callsign, func.count(Log.callsign).label('pcs')).group_by(Log.callsign).order_by('pcs').all()
    temp = list()
    for i in q:
        temp.append(i)
    return [list(elem) for elem in temp]"""

"""def getBandsOccurance():
    q = session.query(Log.band, func.count(Log.band).label('pcs')).group_by(Log.band).order_by('pcs').all()
    temp = list()
    for i in q:
        temp.append(i)
    return [list(elem) for elem in temp]"""

"""def getModeOccurance():
    q = session.query(Log.mode, func.count(Log.mode).label('pcs')).group_by(Log.mode).order_by('pcs').all()
    temp = list()
    for i in q:
        temp.append(i)
    return [list(elem) for elem in temp]"""

def qsoListBandModeByCallsign(callsign):

    q = session.query(Log).where(Log.callsign == callsign.upper())
    temp = list()
    for i in q:
        temp.append({"band":i.band, "mode":i.mode})
    return temp
    
    """qsos = query(callsign)

    res = list()
    for i in qsos:
        #print(i)
        res.append([i["band"], i["mode"]])
        
    return res"""


"""def validQso(nr, orMore=False):
    res = list()
    for callsign in getAllParticipant():
        qsos = qsoListBandModeByCallsign(callsign)
        qsos_unique = [list(x) for x in set(tuple(x) for x in qsos)]
        if orMore == False:
            if len(qsos_unique) == nr:
                res.append(callsign)
        else:
            if len(qsos_unique) >= nr:
                res.append(callsign)
    return res"""

def diplomaDownload(callsign):
    aaa = DiplomaDownload(callsign=callsign,
                          timestamp_utc=getCurrentUtcTs())
    session.add(aaa)
    session.commit()    

def getDownloadedDiplomas():
    q = session.query(DiplomaDownload).all()
    res = [[i.timestamp_utc, i.callsign] for i in q]
    return res

def activateBand(callsign, band, mode):
    aaa = ActiveBand(callsign = callsign,
                     mode = mode,
                     band = band,
                     start_timestamp_utc = getCurrentUtcTs())
    session.add(aaa)
    session.commit()    

def sbActivatedBand(callsign):
    aaa = session.query(ActiveBand) \
        .where(ActiveBand.callsign == callsign,
               ActiveBand.end_timestamp_utc == None)
    return len(aaa.all()) > 0

def isBandActive(callsign, band, mode):
    aaa = session.query(ActiveBand) \
        .where(ActiveBand.band == band,
               ActiveBand.mode == mode,
               ActiveBand.end_timestamp_utc == None)
        #.where(ActiveBand.callsign == callsign,
        #       ActiveBand.band == band,
        #       ActiveBand.mode == mode,
        #       ActiveBand.end_timestamp_utc == None)
    return len(aaa.all()) > 0

def deactivateBand(callsign, band, mode):
    session.query(ActiveBand) \
        .where(ActiveBand.callsign == callsign,
               ActiveBand.band == band,
               ActiveBand.mode == mode) \
        .update({"end_timestamp_utc": getCurrentUtcTs()})
    session.commit() 

def getActiveBands():
    aaa = session.query(ActiveBand) \
        .where(ActiveBand.end_timestamp_utc == None) \
        .all()
    return [{"callsign":i.callsign, "mode":i.mode, "band": i.band} for i in aaa]

def getActiveBandsHistory():
    aaa = session.query(ActiveBand).all()
    return [{"callsign":i.callsign, 
             "mode":i.mode, 
             "band": i.band, 
             "start_timestamp_utc":i.start_timestamp_utc,
             "end_timestamp_utc":i.end_timestamp_utc} for i in aaa]



if __name__ == "__main__":
    #print(getAllParticipant())
    #diplomaDownload("callsign")
    #getDownloadedDiplomas()

    """print("active", isBandActive("ha1mp", "2m", "ssb"))
    activateBand("ha1mp", "2m", "ssb")
    print("active", isBandActive("ha1mp", "2m", "ssb"))
    print("---------", getActiveBands())
    deactivateBand("ha1mp", "2m", "ssb")
    print("---------", getActiveBands())
    print("active", isBandActive("ha1mp", "2m", "ssb"))"""


    #print(getAllParticipant())
    print(query("ha1wd"))

