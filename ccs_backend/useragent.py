"""User-Agent -> böngésző / operációs rendszer / bot feldolgozás.

Elsődlegesen a `user_agents` csomagot használja (pontos, karbantartott
szabálykészlet). Ha az nincs telepítve, egy egyszerű regex-alapú tartalékra
esik vissza, hogy a látogatószámláló e nélkül is működjön.
"""

import re

try:
    from user_agents import parse as _ua_parse
    _HAS_LIB = True
except Exception:
    _HAS_LIB = False


# Egyszerű bot-felismerés a tartalék ághoz (a user_agents ezt maga tudja).
_BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|embedly|"
    r"quora|pinterest|vkshare|whatsapp|telegrambot|discordbot|"
    r"headlesschrome|python-requests|curl|wget|axios|go-http",
    re.IGNORECASE,
)


def _fallback(ua):
    """Nagyon egyszerű parse, ha nincs user_agents csomag."""
    is_bot = bool(_BOT_RE.search(ua))

    # Böngésző (sorrend számít: az Edge/Opera a Chrome-ot is tartalmazza).
    browser = "Ismeretlen"
    for name, pat in [
        ("Edge", r"edg(?:e|a|ios)?/"),
        ("Opera", r"opr/|opera"),
        ("Samsung Internet", r"samsungbrowser"),
        ("Chrome", r"chrome/|crios/"),
        ("Firefox", r"firefox/|fxios/"),
        ("Safari", r"version/.*safari"),
    ]:
        if re.search(pat, ua, re.IGNORECASE):
            browser = name
            break

    # Operációs rendszer.
    os_name = "Ismeretlen"
    for name, pat in [
        ("Android", r"android"),
        ("iOS", r"iphone|ipad|ipod"),
        ("Windows", r"windows nt|windows"),
        ("macOS", r"mac os x|macintosh"),
        ("Linux", r"linux"),
        ("Chrome OS", r"cros"),
    ]:
        if re.search(pat, ua, re.IGNORECASE):
            os_name = name
            break

    return {"browser": browser, "os": os_name, "is_bot": is_bot}


def parse(ua):
    """Visszaad: {'browser', 'os', 'is_bot'}. Üres UA-t botként kezel."""
    ua = (ua or "").strip()
    if not ua:
        return {"browser": "Ismeretlen", "os": "Ismeretlen", "is_bot": True}

    if not _HAS_LIB:
        return _fallback(ua)

    try:
        parsed = _ua_parse(ua)
        browser = parsed.browser.family or "Ismeretlen"
        os_name = parsed.os.family or "Ismeretlen"
        # A user_agents is_bot mellé a saját regexünk is (kettős védelem).
        is_bot = bool(parsed.is_bot) or bool(_BOT_RE.search(ua))
        return {"browser": browser, "os": os_name, "is_bot": is_bot}
    except Exception:
        return _fallback(ua)
