"""Egyszerű, függőség nélküli admin hitelesítés a CCS backendhez.

A felhasználónév/jelszó párosok és a token beállításai a `config.py`-ból jönnek
(korábban a `users.json`-ból). Sikeres bejelentkezéskor egy aláírt, lejárati
idővel ellátott token jön létre (HMAC-SHA256), amit a védett végpontok az
`Authorization: Bearer <token>` fejlécben várnak.
"""

import time
import hmac
import base64
import hashlib

from fastapi import HTTPException, Header

import config


def verify_credentials(username, password):
    """Igaz, ha a felhasználónév/jelszó páros szerepel a beállításokban."""
    normalized_username = str(username).strip().lower()
    stored = config.getUsers().get(normalized_username)
    if stored is None:
        return False
    return hmac.compare_digest(stored.lower(), str(password).lower())


def _sign(payload):
    secretKey = config.getAuthSecret()
    sig = hmac.new(secretKey.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")


def create_token(username):
    """Aláírt token létrehozása a felhasználónak, lejárati idővel."""
    expiry = int(time.time()) + config.getAuthTtl()
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
