from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User

COOKIE_NAME = "urban_session"

def create_token(user: User) -> str:
    payload = {
        "id": user.id, "name": user.name, "phone": user.phone,
        "role": user.role, "agency": user.agency,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_expire_seconds),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def get_session(request: Request):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def require_auth(request: Request):
    session = get_session(request)
    if not session:
        raise HTTPException(401, "احراز هویت لازم است")
    return session

def require_role(*roles):
    def dependency(request: Request):
        session = require_auth(request)
        if session.get("role") not in roles:
            raise HTTPException(403, "دسترسی مجاز نیست")
        return session
    return dependency

def set_session(response: Response, user: User):
    response.set_cookie(
        COOKIE_NAME, create_token(user), httponly=True, secure=settings.cookie_secure,
        samesite="lax", path="/", max_age=settings.jwt_expire_seconds
    )
