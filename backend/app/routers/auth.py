from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from ..auth import COOKIE_NAME, get_session
from ..db import get_db
from ..schemas import AuthRequest
from ..services.auth_service import AuthService

router = APIRouter()


@router.post("/api/auth")
def auth(body: AuthRequest, response: Response, db: Session = Depends(get_db)):
    return AuthService(db).authenticate(body, response)


@router.delete("/api/auth")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"message": "خروج موفقیت‌آمیز بود"}


@router.get("/api/auth/me")
def me(request: Request):
    return {"user": get_session(request)}
