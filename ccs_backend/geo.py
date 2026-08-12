"""IP -> ország feloldás a MaxMind GeoLite2 ONLINE web service-én keresztül.

A `geoip2` library `webservice.Client`-jét használjuk: minden (még nem
gyorsítótárazott) IP-hez egy HTTPS-hívás megy a MaxMind felé, tehát nem kell
helyi `.mmdb` fájlt karbantartani.

Szükséges (ingyenes GeoLite2 web service, MaxMind fiókkal):
    CCS_GEOIP_ACCOUNT_ID   - a MaxMind account ID
    CCS_GEOIP_LICENSE_KEY  - a MaxMind license key
    CCS_GEOIP_HOST         - alapértelmezés: geolite.info (a GeoLite2 web service)

Ha a csomag / a hitelesítő adatok hiányoznak, vagy a hívás hibázik, a modul
némán "Ismeretlen"-t ad vissza, tehát a látogatószámláló e nélkül is működik
(csak ország nélkül).

FIGYELEM: a backend konténernek KIFELÉ menő internetkapcsolat kell ehhez
(a MaxMind eléréséhez). Lásd a docker-compose.yml megjegyzését.
"""

import ipaddress

import config

# Minden beállítás a config.py-ból: fiókadatok, a használt host (ingyenes
# GeoLite2: geolite.info), a hívás időkorlátja, és a bőbeszédű naplózás
# kapcsolója (enélkül csak a tényleges lookup-hibákat naplózzuk).
_settings = config.getGeoip()

DEBUG = _settings["debug"]
ACCOUNT_ID = _settings["account_id"]
LICENSE_KEY = _settings["license_key"]
HOST = _settings["host"]
TIMEOUT = _settings["timeout"]

UNKNOWN = "Ismeretlen"

_client = None
_tried = False

# Egyszerű, folyamat-szintű gyorsítótár: IP -> ország. Így ugyanazt az IP-t nem
# kérdezzük le újra és újra (kevesebb késleltetés és kevesebb API-lekérés).
_cache = {}
_CACHE_MAX = 10000


def _get_client():
    """A geoip2 web service kliens lusta létrehozása. Hiba/hiányzó adat -> None."""
    global _client, _tried
    if _tried:
        return _client
    _tried = True

    if not ACCOUNT_ID or not LICENSE_KEY:
        print("[geo] Nincs CCS_GEOIP_ACCOUNT_ID / CCS_GEOIP_LICENSE_KEY; "
              f"az ország mindig '{UNKNOWN}' lesz.")
        _client = None
        return None

    try:
        import geoip2.webservice
        _client = geoip2.webservice.Client(
            int(ACCOUNT_ID),
            LICENSE_KEY,
            host=HOST,
            timeout=TIMEOUT,
        )
        print(f"[geo] GeoLite2 web service kliens kész (host={HOST}).")
    except Exception as e:  # geoip2 hiányzik, rossz account id, stb.
        print(f"[geo] GeoLite2 web service nem elérhető ({e}); az ország '{UNKNOWN}' lesz.")
        _client = None
    return _client


def _is_private(ip):
    """Privát / lokális / nem publikus IP? Ezeket a MaxMind nem tudja
    geolokálni (localhost, LAN, docker-belső hálózat, stb.)."""
    try:
        addr = ipaddress.ip_address(ip)
        return (addr.is_private or addr.is_loopback or addr.is_reserved
                or addr.is_link_local or addr.is_unspecified)
    except ValueError:
        return False


def country_of(ip):
    """Az IP-hez tartozó ország neve (angolul), vagy 'Ismeretlen'.

    Privát / lokális / feloldhatatlan címeknél és bármilyen hibánál is
    'Ismeretlen'-t ad. Az eredményt IP szerint gyorsítótárazza.
    """
    if not ip:
        return UNKNOWN

    if ip in _cache:
        return _cache[ip]

    # Privát / lokális IP-t (localhost, LAN, docker) online nem lehet feloldani.
    # Ez a leggyakoribb oka a fejlesztés közbeni "Ismeretlen"-nek.
    if _is_private(ip):
        if DEBUG:
            print(f"[geo] privát/lokális IP, nem geolokálható: {ip}")
        _cache[ip] = UNKNOWN
        return UNKNOWN

    client = _get_client()
    if client is None:
        return UNKNOWN

    try:
        resp = client.country(ip)
        result = resp.country.name or UNKNOWN
        if DEBUG:
            print(f"[geo] {ip} -> {result}")
    except Exception as e:
        # AddressNotFoundError, AuthenticationError, OutOfQueriesError,
        # hálózati hiba, stb. -> ne dőljön el a /hit, de NAPLÓZZUK az okot,
        # hogy látszódjon, miért lett "Ismeretlen".
        print(f"[geo] lookup hiba (ip={ip}): {type(e).__name__}: {e}")
        result = UNKNOWN

    # Gyorsítótár korlátozása (egyszerű: túlcsordulásnál ürítjük).
    if len(_cache) >= _CACHE_MAX:
        _cache.clear()
    _cache[ip] = result
    return result
