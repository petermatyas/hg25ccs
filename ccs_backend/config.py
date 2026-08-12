"""A backend ÖSSZES beállítása egy helyen.

Ide tartozik az aktiválás adata (hívójel, állomásadatok), az admin belépők, a
naplózáshoz használt sáv/mód listák, a diploma feltétele, valamint a titkok és
a külső szolgáltatások paraméterei. A többi modul nem olvas se fájlt, se
környezeti változót – mindent innen kér el.

Két szint van:

* az itt felvett érték (ez a "config fájl" tartalma), és
* a környezeti változó, ami felülírja – így éles környezetben a titkok a
  docker-compose `environment` / `env_file` részéből jönnek, és nem kerülnek
  verziókövetésbe.

A beállításokat szándékosan függvények adják vissza, nem konstansként exportál-
juk őket: így akkor is a friss értéket kapjuk, ha a környezet a modul betöltése
után áll össze, és a hívási hely mindig egyértelmű.
"""

import os


# ---------------------------------------------------------------------------
# Az aktiválás
# ---------------------------------------------------------------------------

# A saját hívójel: erről ismerjük fel a naplókban, melyik mező NEM az ellen-
# állomás, és ez kerül a diplomára, a QSL lapra és a letöltött fájlnevekbe.
ACTIVATION_CALLSIGN = "hg25ccs"

# A QSL lapon megjelenő állomásadatok.
STATION = {
    "itu": "28",
    "cq": "15",
    "qth": "SZOMBATHELY, HUNGARY",
    "locator": "JN87GF",
}


# ---------------------------------------------------------------------------
# Admin belépők (korábban users.json)
# ---------------------------------------------------------------------------

# Az admin felület felhasználói. A jelszó itt nyílt szövegként áll, ezért a
# fájl NE kerüljön publikus repóba; élesben a CCS_USERS környezeti változóval
# írható felül, 'felhasznalo:jelszo' párokkal, vesszővel elválasztva.
USERS = [
    {"username": "ha1mp",  "password": "ha1vhf"},
    {"username": "ha1nbs", "password": "ha1vhf"},
    {"username": "ha1nb",  "password": "ha1vhf"},
    {"username": "ha1wd",  "password": "ha1vhf"},
    {"username": "ha1ls",  "password": "ha1vhf"},
    {"username": "ha1tib", "password": "ha1vhf"},
]


# ---------------------------------------------------------------------------
# Napló és diploma
# ---------------------------------------------------------------------------

BANDS = ["70cm", "2m", "4m", "6m", "10m", "12m", "15m", "17m", "20m", "30m",
         "40m", "60m", "80m", "160m"]

MODES = ["CW", "SSB", "FM", "DIGI"]

# Ennyi KÜLÖNBÖZŐ (sáv, mód) párosítás kell a diplomához.
MIN_VALID_QSO = 3

# Kézzel felvett kivételek: ezek a hívójelek a QSO-számtól függetlenül kapnak
# diplomát (kisbetűvel).
EXTRA_DIPLOMA_LIST = []


# ---------------------------------------------------------------------------
# Titkok és külső szolgáltatások (élesben környezeti változóból)
# ---------------------------------------------------------------------------

AUTH_SECRET = "change-this-ccs-admin-secret"
AUTH_TTL = 12 * 60 * 60                       # token élettartam másodpercben
ANALYTICS_SALT = "change-this-ccs-analytics-salt"

# A feltöltött naplófájlok mappája; üresen a backend melletti "logs".
LOGS_DIR = ""

# GeoLite2 web service a látogatók országának feloldásához.
GEOIP = {
    "account_id": "",
    "license_key": "",
    "host": "geolite.info",
    "timeout": 2.0,
    "debug": False,
}


# ---------------------------------------------------------------------------
# Olvasók
# ---------------------------------------------------------------------------

def _env(name, fallback=""):
    """Környezeti változó levágott értéke, üres esetén a megadott alapérték."""
    return os.environ.get(name, "").strip() or fallback


def getActivationCallsign():
    """Az aktiválás hívójele (CCS_ACTIVATION_CALLSIGN)."""
    return _env("CCS_ACTIVATION_CALLSIGN", ACTIVATION_CALLSIGN)


def getStation():
    """A QSL lapon megjelenő állomásadatok (ITU, CQ, QTH, lokátor).

    Mezőnként felülírható: CCS_STATION_ITU, CCS_STATION_CQ, CCS_STATION_QTH,
    CCS_STATION_LOCATOR.
    """
    return {
        "itu": _env("CCS_STATION_ITU", STATION["itu"]),
        "cq": _env("CCS_STATION_CQ", STATION["cq"]),
        "qth": _env("CCS_STATION_QTH", STATION["qth"]),
        "locator": _env("CCS_STATION_LOCATOR", STATION["locator"]),
    }


def getUsers():
    """Az admin belépők {felhasználónév: jelszó} alakban (kisbetűs nevekkel).

    A CCS_USERS környezeti változó felülírja: 'nev:jelszo,nev2:jelszo2'.
    """
    users = dict()

    raw = _env("CCS_USERS")
    if raw:
        for entry in raw.split(","):
            if ":" not in entry:
                continue
            username, password = entry.split(":", 1)
            if username.strip():
                users[username.strip().lower()] = password.strip()
        return users

    for entry in USERS:
        username = entry.get("username")
        password = entry.get("password")
        if username and password is not None:
            users[str(username).strip().lower()] = str(password)

    return users


def getOperators():
    """A helyi operátorok (az admin felhasználók) hívójele, ábécésorrendben."""
    return sorted(getUsers().keys())


def getBands():
    """A statisztikában ismert sávok."""
    return list(BANDS)


def getModes():
    """A statisztikában ismert módok."""
    return sorted(MODES)


def getMinValidQso():
    """A diplomához szükséges különböző (sáv, mód) párosítások száma."""
    minValidQso = _env("CCS_MIN_VALID_QSO")
    if minValidQso.isdigit():
        return int(minValidQso)

    return MIN_VALID_QSO


def getExtraDiplomaList():
    """A QSO-számtól függetlenül diplomát kapó hívójelek (kisbetűvel)."""
    extraDiplomaList = _env("CCS_EXTRA_DIPLOMA_LIST")
    if extraDiplomaList:
        return [i.strip().lower() for i in extraDiplomaList.split(",") if i.strip()]

    return [str(i).strip().lower() for i in EXTRA_DIPLOMA_LIST]


def getAuthSecret():
    """A tokenek aláírásához használt titok (CCS_AUTH_SECRET)."""
    return _env("CCS_AUTH_SECRET", AUTH_SECRET)


def getAuthTtl():
    """A token élettartama másodpercben (CCS_AUTH_TTL)."""
    ttl = _env("CCS_AUTH_TTL")
    if ttl.isdigit():
        return int(ttl)

    return AUTH_TTL


def getAnalyticsSalt():
    """A látogató-azonosító hash sója (CCS_ANALYTICS_SALT)."""
    return _env("CCS_ANALYTICS_SALT", ANALYTICS_SALT)


def getLogsDir():
    """A feltöltött naplófájlok mappája (CCS_LOGS_DIR), abszolút útvonalként."""
    logsDir = _env("CCS_LOGS_DIR", LOGS_DIR)
    if not logsDir:
        logsDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs")

    return os.path.abspath(logsDir)


def getGeoip():
    """A GeoLite2 web service beállításai."""
    try:
        timeout = float(_env("CCS_GEOIP_TIMEOUT", str(GEOIP["timeout"])))
    except ValueError:
        timeout = GEOIP["timeout"]

    return {
        "account_id": _env("CCS_GEOIP_ACCOUNT_ID", GEOIP["account_id"]),
        "license_key": _env("CCS_GEOIP_LICENSE_KEY", GEOIP["license_key"]),
        "host": _env("CCS_GEOIP_HOST", GEOIP["host"]),
        "timeout": timeout,
        "debug": _env("CCS_GEOIP_DEBUG", str(GEOIP["debug"])).lower() in ("1", "true", "yes"),
    }
