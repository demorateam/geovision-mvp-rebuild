from secrets import randbelow
from time import time

_store: dict[str, dict] = {}
_last: dict[str, float] = {}
TTL = 120
COOLDOWN = 30
MAX_ATTEMPTS = 5

def generate(phone: str) -> str:
    now = time()
    if now - _last.get(phone, 0) < COOLDOWN:
        raise ValueError("OTP_RATE_LIMIT")
    code = str(10000 + randbelow(90000))
    _store[phone] = {"code": code, "expires": now + TTL, "attempts": 0}
    _last[phone] = now
    return code

def verify(phone: str, code: str) -> bool:
    entry = _store.get(phone)
    if not entry or time() > entry["expires"]:
        _store.pop(phone, None); return False
    entry["attempts"] += 1
    ok = entry["code"] == code
    if ok or entry["attempts"] >= MAX_ATTEMPTS:
        _store.pop(phone, None)
    return ok
