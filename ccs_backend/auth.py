"""Egyszerű, függőség nélküli admin hitelesítés a CCS backendhez.

A felhasználónév/jelszó párosokat a `users.json` fájl tartalmazza (induláskor
ebből töltődnek be). Sikeres bejelentkezéskor egy aláírt, lejárati idővel
ellátott token jön létre (HMAC-SHA256), amit a védett végpontok az
`Authorization: Bearer <token>` fejlécben várnak.
"""

import os
import json
import time
import hmac
import base64
import hashlib

from fastapi import HTTPException, Header

baseDir = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(baseDir, "users.json")

# Token élettartam másodpercben (alapértelmezés: 12 óra).
TOKEN_TTL = int(os.environ.get("CCS_AUTH_TTL", str(12 * 60 * 60)))

# A tokenek aláírásához használt titkos kulcs. Élesben érdemes a
# CCS_AUTH_SECRET környezeti változóban beállítani.
SECRET_KEY = os.environ.get("CCS_AUTH_SECRET", "change-this-ccs-admin-secret")


def _load_users():
    """Felhasználónév -> jelszó páros betöltése a users.json fájlból."""
    if not os.path.exists(USERS_FILE):
        print(f"[auth] FIGYELEM: nem található a users.json ({USERS_FILE})")
        return {}

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    users = {}
    for entry in data.get("users", []):
        username = entry.get("username")
        password = entry.get("password")
        if username and password is not None:
            users[username] = str(password)
    return users


_USERS = _load_users()


def verify_credentials(username, password):
    """Igaz, ha a felhasználónév/jelszó páros szerepel a users.json-ban."""
    stored = _USERS.get(username)
    if stored is None:
        return False
    return hmac.compare_digest(stored, str(password))


def _sign(payload):
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")


def create_token(username):
    """Aláírt token létrehozása a felhasználónak, lejárati idővel."""
    expiry = int(time.time()) + TOKEN_TTL
    payload = f"{username}:{expiry}"
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    return f"{payload_b64}.{_sign(payload)}"


def verify_token(token):
    """A token visszafejtése és ellenőrzése. Érvényes esetén a felhasználónevet
    adja vissza, egyébként None-t."""
    try:
        payload_b64, signature = token.split(".")
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = base64.urlsafe_b64decode(padded).decode()
        username, expiry = payload.rsplit(":", 1)
    except (ValueError, AttributeError):
        return None

    if not hmac.compare_digest(_sign(payload), signature):
        return None
    if int(expiry) < int(time.time()):
        return None
    return username


def require_auth(authorization: str = Header(default="")):
    """FastAPI dependency: érvényes Bearer token megkövetelése."""
    token = ""
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Bejelentkezés szükséges")
    return username
