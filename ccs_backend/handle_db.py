from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import select, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager
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
    visitor_hash = Column(String)   # a letöltő látogató pszeudonim azonosítója


class QslDownload(Base):
    __tablename__ = 'qslDownload'
    id = Column(Integer, primary_key=True)
    callsign = Column(String)
    qso_timestamp_utc = Column(Integer)
    timestamp_utc = Column(Integer)
    visitor_hash = Column(String)   # a letöltő látogató pszeudonim azonosítója


class Setting(Base):
    """Egyszerű kulcs-érték beállítástár (pl. az oldal aktiválási állapota)."""
    __tablename__ = 'setting'
    key = Column(String, primary_key=True)
    value = Column(String)


class Visit(Base):
    """Egy oldalletöltés (page view) a saját, süti-mentes látogatószámlálóból.

    Nyers IP-t NEM tárolunk, csak a belőle (+ user agentből) képzett stabil
    hasht (`visitor_hash`), így a látogatók megkülönböztethetők anélkül, hogy
    személyes adatot őriznénk.
    """
    __tablename__ = 'visit'
    id = Column(Integer, primary_key=True)
    timestamp_utc = Column(Integer)
    day = Column(String)            # 'YYYY-MM-DD' (UTC) — a napi bontáshoz
    path = Column(String)           # melyik oldal
    referrer = Column(String)       # honnan érkezett (domain)
    visitor_hash = Column(String)   # pszeudonim látogató-azonosító (NEM IP)
    is_returning = Column(Integer)  # 1, ha ezt a hasht már láttuk korábban
    country = Column(String)        # GeoLite2 alapján, csak ország
    browser = Column(String)
    os = Column(String)
    device_type = Column(String)    # mobil / tablet / desktop
    language = Column(String)       # navigator.language (pl. 'hu', 'en-US')
    timezone = Column(String)       # böngésző időzónája (pl. 'Europe/Budapest')
    connection_type = Column(String)  # 4g / wifi / 3g ... (ha a böngésző adja)
    screen_w = Column(Integer)
    screen_h = Column(Integer)
    viewport_w = Column(Integer)
    viewport_h = Column(Integer)
    device_pixel_ratio = Column(String)
    load_time_ms = Column(Integer)     # oldal betöltési ideje (ms)
    time_on_page_ms = Column(Integer)  # oldalon töltött idő (ms), kilépéskor
    scroll_depth = Column(Integer)     # maximális görgetési mélység (%)
    is_bot = Column(Integer)        # 1, ha keresőrobotnak tűnik


class ClickEvent(Base):
    """Egy kattintás-esemény (pl. keresés gomb, letöltés link)."""
    __tablename__ = 'clickEvent'
    id = Column(Integer, primary_key=True)
    timestamp_utc = Column(Integer)
    day = Column(String)
    visitor_hash = Column(String)
    path = Column(String)
    event = Column(String)          # az esemény címkéje (pl. 'diploma_search')


class SearchEvent(Base):
    """Egy publikus hívójel-keresés (az index-oldali kereséskor)."""
    __tablename__ = 'searchEvent'
    id = Column(Integer, primary_key=True)
    timestamp_utc = Column(Integer)
    day = Column(String)
    visitor_hash = Column(String)
    callsign = Column(String)



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


def _migrate_schema():
    """Egyszerű, függőség nélküli SQLite migráció.

    A create_all() a HIÁNYZÓ TÁBLÁKAT létrehozza, de a MÁR LÉTEZŐ táblákhoz
    (pl. visit, diplomaDownload, qslDownload egy korábbi verzióból) nem ad
    hozzá új oszlopot. Itt PRAGMA-val megnézzük a meglévő oszlopokat, és
    ALTER TABLE ADD COLUMN-nal pótoljuk a hiányzókat. Idempotens: többszöri
    futtatás is biztonságos.
    """
    import sqlite3
    conn = sqlite3.connect(databasePath)
    cur = conn.cursor()

    # WAL napló: több párhuzamos olvasó + egy író jól megfér egymás mellett,
    # ami a session-önkénti (rövid életű) írásoknál csökkenti a "database is
    # locked" eséllyét. A beállítás perzisztens a DB fájlban.
    try:
        cur.execute("PRAGMA journal_mode=WAL")
    except Exception:
        pass

    def table_exists(name):
        row = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)
        ).fetchone()
        return row is not None

    def columns(table):
        return {r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()}

    def add_missing(table, cols):
        if not table_exists(table):
            return
        existing = columns(table)
        for col, decl in cols.items():
            if col not in existing:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
                print(f"[migrate] {table}.{col} ({decl}) hozzáadva")

    add_missing("visit", {
        "device_type": "TEXT",
        "language": "TEXT",
        "timezone": "TEXT",
        "connection_type": "TEXT",
        "load_time_ms": "INTEGER",
        "time_on_page_ms": "INTEGER",
        "scroll_depth": "INTEGER",
    })
    add_missing("diplomaDownload", {"visitor_hash": "TEXT"})
    add_missing("qslDownload", {"visitor_hash": "TEXT"})

    conn.commit()
    conn.close()


_migrate_schema()


Session = sessionmaker(bind=engine)
session = Session()


@contextmanager
def _db():
    """Rövid életű, izolált session egy művelethez (thread-biztos).

    A modul-szintű globális `session` egyetlen objektum, amit a FastAPI
    threadpool több szála PÁRHUZAMOSAN használ. A gyakori analytics-írások
    (/hit, /event) így versenyhelyzetbe kerülnek: egy elbukott flush
    'megmérgezi' a közös session-t (PendingRollbackError), és onnantól minden
    kérés elhal. Ezért az analytics- és letöltés-műveletek külön, friss
    session-t kapnak, commit/rollback/close kezeléssel."""
    s = Session()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


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

def exportLogs():
    q = session.query(Log).all()
    return [{
        "callsign": i.callsign,
        "band": i.band,
        "mode": i.mode,
        "qth": i.qth,
        "log_timestamp_utc": i.log_timestamp_utc,
        "upload_timestamp_utc": i.upload_timestamp_utc,
        "uploaded_filename": i.uploaded_filename,
        "rst_sent": i.rst_sent,
        "rst_rec": i.rst_rec,
        "local_operator": i.local_operator,
        "error": i.error,
    } for i in q]

def importLogs(logList):
    added = 0
    for log in logList:
        exists = session.query(Log).where(
            Log.callsign == log.get("callsign"),
            Log.band == log.get("band"),
            Log.mode == log.get("mode"),
            Log.qth == log.get("qth"),
            Log.rst_sent == log.get("rst_sent"),
            Log.rst_rec == log.get("rst_rec"),
            Log.log_timestamp_utc == log.get("log_timestamp_utc"),
            Log.local_operator == log.get("local_operator"),
        ).first()
        if exists is None:
            session.add(Log(
                callsign=log.get("callsign"),
                band=log.get("band"),
                mode=log.get("mode"),
                qth=log.get("qth"),
                log_timestamp_utc=log.get("log_timestamp_utc"),
                upload_timestamp_utc=log.get("upload_timestamp_utc"),
                uploaded_filename=log.get("uploaded_filename"),
                rst_sent=log.get("rst_sent"),
                rst_rec=log.get("rst_rec"),
                local_operator=log.get("local_operator"),
                error=log.get("error"),
            ))
            added += 1
    session.commit()
    return added

def clearAllLogs():
    n = session.query(Log).delete()
    session.commit()
    return n

def replaceDatabase(fileBytes):
    session.close()
    engine.dispose()
    with open(databasePath, "wb") as fileObj:
        fileObj.write(fileBytes)

def removeLogs(uploadTimestamp, filename):
    session.query(Log).where(Log.upload_timestamp_utc==uploadTimestamp and Log.uploaded_filename==filename).delete()
    session.commit() 

def query(callsign):

   with _db() as s:
        q = s.query(Log).where(Log.callsign.ilike(f"%{callsign}%"))

        temp = list()
        for i in q:
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

def diplomaDownload(callsign, visitor_hash=None):
    with _db() as s:
        s.add(DiplomaDownload(callsign=_canonCallsign(callsign),
                              timestamp_utc=getCurrentUtcTs(),
                              visitor_hash=visitor_hash))

def getDownloadedDiplomas():
    with _db() as s:
        q = s.query(DiplomaDownload).all()
        return [[i.timestamp_utc, i.callsign] for i in q]

def _canonCallsign(callsign):
    return callsign.upper().replace("/", "_")

def isDiplomaDownloaded(callsign):
    c = _canonCallsign(callsign)
    with _db() as s:
        return s.query(DiplomaDownload).where(DiplomaDownload.callsign == c).first() is not None

def qslDownload(callsign, qso_timestamp, visitor_hash=None):
    with _db() as s:
        s.add(QslDownload(callsign=_canonCallsign(callsign),
                          qso_timestamp_utc=int(qso_timestamp),
                          timestamp_utc=getCurrentUtcTs(),
                          visitor_hash=visitor_hash))

def getDownloadedQslTimestamps(callsign):
    c = _canonCallsign(callsign)
    with _db() as s:
        q = s.query(QslDownload.qso_timestamp_utc).where(QslDownload.callsign == c).all()
        return set(int(i[0]) for i in q)

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


# ---- Beállítások (kulcs-érték) ----

def getSetting(key, default=None):
    with _db() as s:
        row = s.query(Setting).where(Setting.key == key).first()
        return row.value if row is not None else default

def setSetting(key, value):
    with _db() as s:
        row = s.query(Setting).where(Setting.key == key).first()
        if row is None:
            s.add(Setting(key=key, value=str(value)))
        else:
            row.value = str(value)

# Az oldal (index.html-en a keresés) aktiválási állapota. Alapból inaktív:
# amíg az admin nem aktiválja, az index.html keresés nem működik.
def getSiteActive():
    return getSetting("site_active", "0") == "1"

def setSiteActive(active):
    setSetting("site_active", "1" if active else "0")
    return getSiteActive()


# ---- Látogatottság (page view számláló) ----

def addVisit(fields: dict):
    """Egy oldalletöltés rögzítése.

    `fields` várt kulcsai: timestamp_utc, day, path, referrer, visitor_hash,
    country, browser, os, screen_w, screen_h, viewport_w, viewport_h,
    device_pixel_ratio, is_bot. A `is_returning` értéket itt számoljuk ki:
    igaz, ha ezt a visitor_hasht már láttuk korábban.
    """
    visitor_hash = fields.get("visitor_hash")
    with _db() as s:
        seen_before = False
        if visitor_hash:
            seen_before = s.query(Visit.id) \
                .where(Visit.visitor_hash == visitor_hash) \
                .first() is not None

        v = Visit(
            timestamp_utc=fields.get("timestamp_utc", getCurrentUtcTs()),
            day=fields.get("day"),
            path=fields.get("path"),
            referrer=fields.get("referrer"),
            visitor_hash=visitor_hash,
            is_returning=1 if seen_before else 0,
            country=fields.get("country"),
            browser=fields.get("browser"),
            os=fields.get("os"),
            device_type=fields.get("device_type"),
            language=fields.get("language"),
            timezone=fields.get("timezone"),
            connection_type=fields.get("connection_type"),
            screen_w=fields.get("screen_w"),
            screen_h=fields.get("screen_h"),
            viewport_w=fields.get("viewport_w"),
            viewport_h=fields.get("viewport_h"),
            device_pixel_ratio=fields.get("device_pixel_ratio"),
            is_bot=1 if fields.get("is_bot") else 0,
        )
        s.add(v)
        s.flush()  # az id-t a commit előtt megszerezzük
        return {"id": v.id, "is_returning": seen_before}


def updateVisit(visit_id, time_on_page_ms=None, scroll_depth=None, load_time_ms=None):
    """Egy meglévő látogatás elköteleződési adatainak frissítése (kilépéskor
    küldött beacon). Csak a megadott mezőket írja."""
    with _db() as s:
        row = s.query(Visit).where(Visit.id == visit_id).first()
        if row is None:
            return False
        if time_on_page_ms is not None:
            row.time_on_page_ms = int(time_on_page_ms)
        if scroll_depth is not None:
            row.scroll_depth = int(scroll_depth)
        if load_time_ms is not None:
            row.load_time_ms = int(load_time_ms)
        return True


def addClickEvent(fields: dict):
    """Egy kattintás-esemény rögzítése."""
    with _db() as s:
        s.add(ClickEvent(
            timestamp_utc=fields.get("timestamp_utc", getCurrentUtcTs()),
            day=fields.get("day"),
            visitor_hash=fields.get("visitor_hash"),
            path=fields.get("path"),
            event=fields.get("event"),
        ))


def addSearchEvent(callsign, visitor_hash=None):
    """Egy publikus hívójel-keresés rögzítése."""
    from datetime import datetime as _dt, timezone as _tz
    with _db() as s:
        s.add(SearchEvent(
            timestamp_utc=getCurrentUtcTs(),
            day=_dt.now(_tz.utc).strftime("%Y-%m-%d"),
            visitor_hash=visitor_hash,
            callsign=(callsign or "").upper()[:32],
        ))


def _visitTopCounts(column, base_query, limit=None):
    """Segéd: egy oszlop szerinti csoportosított darabszám, csökkenő sorrendben."""
    stmt = base_query \
        .with_entities(column, func.count(Visit.id).label("cnt")) \
        .group_by(column) \
        .order_by(func.count(Visit.id).desc())
    rows = stmt.all()
    res = [{"key": (r[0] if r[0] is not None else "Ismeretlen"), "count": r[1]} for r in rows]
    if limit is not None:
        res = res[:limit]
    return res


def getVisitStats(include_bots=False):
    """Összesített látogatottsági statisztika az admin nézethez.

    Friss, izolált session-t használ (_db), hogy lássa a más session-ök által
    írt (analytics/letöltés) adatot – a közös session esetleg elavult
    pillanatképet szolgálna ki."""
    with _db() as s:
        base = s.query(Visit)
        if not include_bots:
            base = base.where(Visit.is_bot == 0)

        total_views = base.count()
        unique_visitors = base.with_entities(Visit.visitor_hash).distinct().count()

        # Új vs. visszatérő: az adott oldalletöltés első alkalom volt-e az adott
        # látogatótól. (is_returning=0 -> ekkor láttuk először.)
        returning_views = base.where(Visit.is_returning == 1).count()
        new_views = total_views - returning_views

        # Egyedi visszatérő látogatók száma (akiknek van legalább egy ismételt nézete).
        returning_visitors = base.where(Visit.is_returning == 1) \
            .with_entities(Visit.visitor_hash).distinct().count()

        countries = _visitTopCounts(Visit.country, base)
        browsers = _visitTopCounts(Visit.browser, base)
        systems = _visitTopCounts(Visit.os, base)
        pages = _visitTopCounts(Visit.path, base, limit=20)
        referrers = _visitTopCounts(Visit.referrer, base, limit=20)
        languages = _visitTopCounts(Visit.language, base, limit=20)
        timezones = _visitTopCounts(Visit.timezone, base, limit=20)
        device_types = _visitTopCounts(Visit.device_type, base)
        connection_types = _visitTopCounts(Visit.connection_type, base)

        # Átlagok (elköteleződés). A None értékeket a func.avg kihagyja.
        def _avg(col):
            v = base.with_entities(func.avg(col)).scalar()
            return round(v, 1) if v is not None else None

        avg_load_time_ms = _avg(Visit.load_time_ms)
        avg_time_on_page_ms = _avg(Visit.time_on_page_ms)
        avg_scroll_depth = _avg(Visit.scroll_depth)

        # Felbontás "SZÉLESSÉGxMAGASSÁG" formában.
        res_rows = base.where(Visit.screen_w.isnot(None)) \
            .with_entities(Visit.screen_w, Visit.screen_h, func.count(Visit.id).label("cnt")) \
            .group_by(Visit.screen_w, Visit.screen_h) \
            .order_by(func.count(Visit.id).desc()).all()
        resolutions = [{"key": f"{r[0]}x{r[1]}", "count": r[2]} for r in res_rows]

        # Napi bontás (növekvő időrend).
        day_rows = base.with_entities(Visit.day, func.count(Visit.id).label("cnt")) \
            .group_by(Visit.day).order_by(Visit.day.asc()).all()
        daily = [{"day": r[0], "count": r[1]} for r in day_rows]

        # Kattintás-események (esemény-címke szerint).
        click_rows = s.query(ClickEvent.event, func.count(ClickEvent.id).label("cnt")) \
            .group_by(ClickEvent.event).order_by(func.count(ClickEvent.id).desc()).all()
        clicks = [{"key": (r[0] or "Ismeretlen"), "count": r[1]} for r in click_rows]

        # Keresett hívójelek (leggyakoribb elöl).
        search_rows = s.query(SearchEvent.callsign, func.count(SearchEvent.id).label("cnt")) \
            .group_by(SearchEvent.callsign).order_by(func.count(SearchEvent.id).desc()).limit(50).all()
        searched_callsigns = [{"key": (r[0] or "?"), "count": r[1]} for r in search_rows]

        # Diploma/QSL letöltések összekötve a látogatóval (legutóbbiak elöl).
        def _downloads(model, kind):
            rows = s.query(model).order_by(model.timestamp_utc.desc()).limit(50).all()
            out = []
            for r in rows:
                vh = getattr(r, "visitor_hash", None)
                country = None
                if vh:
                    vrow = s.query(Visit.country).where(Visit.visitor_hash == vh) \
                        .order_by(Visit.timestamp_utc.desc()).first()
                    country = vrow[0] if vrow else None
                out.append({
                    "kind": kind,
                    "callsign": r.callsign,
                    "timestamp_utc": r.timestamp_utc,
                    "visitor_hash": vh,
                    "country": country,
                })
            return out

        downloads = _downloads(DiplomaDownload, "diploma") + _downloads(QslDownload, "qsl")
        downloads.sort(key=lambda d: d["timestamp_utc"] or 0, reverse=True)
        downloads = downloads[:50]

        return {
            "total_views": total_views,
            "unique_visitors": unique_visitors,
            "new_views": new_views,
            "returning_views": returning_views,
            "returning_visitors": returning_visitors,
            "avg_load_time_ms": avg_load_time_ms,
            "avg_time_on_page_ms": avg_time_on_page_ms,
            "avg_scroll_depth": avg_scroll_depth,
            "countries": countries,
            "browsers": browsers,
            "systems": systems,
            "device_types": device_types,
            "languages": languages,
            "timezones": timezones,
            "connection_types": connection_types,
            "resolutions": resolutions,
            "pages": pages,
            "referrers": referrers,
            "clicks": clicks,
            "searched_callsigns": searched_callsigns,
            "downloads": downloads,
            "daily": daily,
        }



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
    print(query("g0tsm"))

