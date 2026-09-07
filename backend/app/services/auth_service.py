from uuid import uuid4

from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from ..auth import set_session
from ..config import settings
from ..models import User
from ..otp import generate, verify
from ..repositories import UserRepository
from ..schemas import AuthRequest


def normalize_name(v):
    return " ".join(v.strip().replace("ي", "ی").replace("ك", "ک").split())


def _portal_error(portal, role=None):
    if portal == "admin":
        raise HTTPException(403, detail={"error": "این حساب دسترسی مدیریتی یا سازمانی ندارد. لطفاً از بخش ورود کاربران وارد شوید.", "suggestedPortal": "citizen"})
    raise HTTPException(403, detail={"error": "این حساب متعلق به اپراتور سازمانی است و امکان ورود از بخش کاربران را ندارد.", "suggestedPortal": "admin" if role == "ADMIN" else None})


class AuthService:
    """OTP-based login/registration flow."""

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def _check_portal(self, portal: str, user: User | None):
        if portal == "admin" and (not user or user.role not in ["ADMIN", "AGENCY"]):
            _portal_error("admin", user.role if user else None)
        if portal == "citizen" and user and user.role != "CITIZEN":
            _portal_error("citizen", user.role)

    def authenticate(self, body: AuthRequest, response: Response):
        user = self.users.get_by_phone(body.phone)
        if not body.name:
            raise HTTPException(400, "نام الزامی است")
        self._check_portal(body.portal, user)
        if user and normalize_name(user.name) != normalize_name(body.name):
            raise HTTPException(403, "نام و شماره موبایل واردشده با یکدیگر مطابقت ندارند")
        if body.action == "request":
            try:
                code = generate(body.phone)
            except ValueError as e:
                if str(e) == "OTP_RATE_LIMIT":
                    raise HTTPException(429, "لطفاً ۳۰ ثانیه تا درخواست کد بعدی صبر کنید")
                raise
            return {"message": "کد آزمایشی ساخته شد" if settings.otp_mode == "demo" else "کد تایید ارسال شد", "demoOtp": code if settings.otp_mode == "demo" else None}
        if not body.code or not verify(body.phone, body.code):
            raise HTTPException(400, "کد تایید نامعتبر یا منقضی شده است")
        user = self.users.get_by_phone(body.phone)
        self._check_portal(body.portal, user)
        if not user:
            user = User(id=uuid4().hex, name=normalize_name(body.name), phone=body.phone, role="CITIZEN")
            self.users.add(user)
        set_session(response, user)
        return {"user": {"id": user.id, "name": user.name, "phone": user.phone, "role": user.role, "agency": user.agency}}
