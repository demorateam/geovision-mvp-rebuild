from pathlib import Path
from uuid import uuid4
from datetime import datetime
import random
from fastapi import FastAPI, Depends, Request, Response, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response as RawResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, text
from .config import settings
from .db import Base, engine, get_db
from .models import User, Incident, IncidentAgency, IncidentStatusHistory
from .schemas import AuthRequest, IncidentCreate, IncidentStatusUpdate, AnalysisRequest, AGENCY_LIST
from .auth import require_auth, require_role, set_session, get_session, COOKIE_NAME
from .otp import generate, verify
from .ai import analyze
from .neshan import search as neshan_search, reverse as neshan_reverse, map_url
from .serializers import incident as serialize_incident

app=FastAPI(title="UEMP Backend", version="1.0.0")

from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(FastAPIHTTPException)
async def api_http_error(request, exc):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        payload = detail
    else:
        payload = {"error": str(detail)}
    return JSONResponse(status_code=exc.status_code, content=payload, headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    msg = exc.errors()[0].get("msg", "اطلاعات نامعتبر") if exc.errors() else "اطلاعات نامعتبر"
    return JSONResponse(status_code=400, content={"error": msg})
origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

Path(settings.upload_dir).mkdir(parents=True,exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)

def normalize_name(v): return " ".join(v.strip().replace("ي","ی").replace("ك","ک").split())

def portal_error(portal, role=None):
    if portal=="admin":
        raise HTTPException(403, detail={"error":"این حساب دسترسی مدیریتی یا سازمانی ندارد. لطفاً از بخش ورود کاربران وارد شوید.","suggestedPortal":"citizen"})
    raise HTTPException(403, detail={"error":"این حساب متعلق به اپراتور سازمانی است و امکان ورود از بخش کاربران را ندارد.","suggestedPortal":"admin" if role=="ADMIN" else None})

@app.get("/api/health")
def health(db: Session=Depends(get_db)):
    try: db.execute(text("SELECT 1"))
    except Exception: raise HTTPException(503,{"status":"error","database":"unavailable"})
    return {"status":"ok","database":"connected","timestamp":datetime.utcnow().isoformat()+"Z"}

@app.post("/api/auth")
def auth(body: AuthRequest, response: Response, db: Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.phone==body.phone))
    if not body.name: raise HTTPException(400,"نام الزامی است")
    if body.portal=="admin" and (not user or user.role not in ["ADMIN","AGENCY"]): portal_error("admin",user.role if user else None)
    if body.portal=="citizen" and user and user.role!="CITIZEN": portal_error("citizen",user.role)
    if user and normalize_name(user.name)!=normalize_name(body.name): raise HTTPException(403,"نام و شماره موبایل واردشده با یکدیگر مطابقت ندارند")
    if body.action=="request":
        try: code=generate(body.phone)
        except ValueError as e:
            if str(e)=="OTP_RATE_LIMIT": raise HTTPException(429,"لطفاً ۳۰ ثانیه تا درخواست کد بعدی صبر کنید")
            raise
        return {"message":"کد آزمایشی ساخته شد" if settings.otp_mode=="demo" else "کد تایید ارسال شد","demoOtp":code if settings.otp_mode=="demo" else None}
    if not body.code or not verify(body.phone,body.code): raise HTTPException(400,"کد تایید نامعتبر یا منقضی شده است")
    user=db.scalar(select(User).where(User.phone==body.phone))
    if body.portal=="admin" and (not user or user.role not in ["ADMIN","AGENCY"]): portal_error("admin",user.role if user else None)
    if body.portal=="citizen" and user and user.role!="CITIZEN": portal_error("citizen",user.role)
    if not user:
        user=User(id=uuid4().hex,name=normalize_name(body.name),phone=body.phone,role="CITIZEN"); db.add(user); db.commit(); db.refresh(user)
    set_session(response,user)
    return {"user":{"id":user.id,"name":user.name,"phone":user.phone,"role":user.role,"agency":user.agency}}

@app.delete("/api/auth")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME,path="/")
    return {"message":"خروج موفقیت‌آمیز بود"}

@app.get("/api/auth/me")
def me(request: Request):
    return {"user":get_session(request)}

@app.get("/api/incidents")
def list_incidents(session=Depends(require_auth), db: Session=Depends(get_db)):
    q=select(Incident).options(joinedload(Incident.reporter),joinedload(Incident.agencies)).order_by(Incident.created_at.desc())
    if session["role"]=="CITIZEN": q=q.where(Incident.reporter_id==session["id"])
    elif session["role"]=="AGENCY": q=q.join(IncidentAgency).where(IncidentAgency.agency_name==session.get("agency",""))
    return {"incidents":[serialize_incident(i) for i in db.scalars(q).unique().all()]}

@app.post("/api/incidents")
def create_incident(body: IncidentCreate, session=Depends(require_role("CITIZEN")), db: Session=Depends(get_db)):
    datepart=datetime.utcnow().strftime("%y%m%d")
    incident_number=f"INC-{datepart}-{random.randint(100000,999999)}"
    while db.scalar(select(Incident).where(Incident.incident_number==incident_number)): incident_number=f"INC-{datepart}-{random.randint(100000,999999)}"
    i=Incident(id=uuid4().hex,incident_number=incident_number,reporter_id=session["id"],image_url=body.imageUrl,description=body.description,
      latitude=body.latitude,longitude=body.longitude,region=body.region or "نامشخص",incident_type=body.incidentType or "نامشخص",
      severity=body.severity or "Medium",color_code=body.colorCode or "Yellow",ai_summary=body.aiSummary,status="PENDING")
    db.add(i)
    for a in body.assignedAgencies or []: db.add(IncidentAgency(id=uuid4().hex,incident_id=i.id,agency_name=a))
    db.add(IncidentStatusHistory(id=uuid4().hex,incident_id=i.id,new_status="PENDING"))
    db.commit(); db.refresh(i)
    i=db.execute(select(Incident).options(joinedload(Incident.agencies),joinedload(Incident.reporter)).where(Incident.id==i.id)).unique().scalar_one()
    return {"incident":serialize_incident(i)}, 201

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id:str, session=Depends(require_auth), db: Session=Depends(get_db)):
    i=db.execute(select(Incident).options(joinedload(Incident.reporter),joinedload(Incident.agencies),joinedload(Incident.status_history)).where(Incident.id==incident_id)).unique().scalar_one_or_none()
    if not i: raise HTTPException(404,"رخداد یافت نشد")
    can=session["role"]=="ADMIN" or (session["role"]=="CITIZEN" and i.reporter_id==session["id"]) or (session["role"]=="AGENCY" and any(a.agency_name==session.get("agency") for a in i.agencies))
    if not can: raise HTTPException(403,"دسترسی مجاز نیست")
    return {"incident":serialize_incident(i,include_history=True)}

@app.patch("/api/incidents/{incident_id}")
def update_incident(incident_id:str, body:IncidentStatusUpdate, session=Depends(require_auth), db: Session=Depends(get_db)):
    i=db.execute(select(Incident).options(joinedload(Incident.agencies),joinedload(Incident.reporter)).where(Incident.id==incident_id)).unique().scalar_one_or_none()
    if not i: raise HTTPException(404,"رخداد یافت نشد")
    can=session["role"]=="ADMIN" or (session["role"]=="AGENCY" and any(a.agency_name==session.get("agency") for a in i.agencies))
    if not can: raise HTTPException(403,"دسترسی مجاز نیست")
    old=i.status; new=body.status or old; i.status=new
    if old!=new: db.add(IncidentStatusHistory(id=uuid4().hex,incident_id=i.id,old_status=old,new_status=new))
    db.commit(); db.refresh(i)
    return {"incident":serialize_incident(i)}

@app.get("/api/stats")
def stats(session=Depends(require_role("ADMIN")), db: Session=Depends(get_db)):
    total=db.scalar(select(func.count()).select_from(Incident)); pending=db.scalar(select(func.count()).select_from(Incident).where(Incident.status=="PENDING"))
    progress=db.scalar(select(func.count()).select_from(Incident).where(Incident.status=="IN_PROGRESS")); resolved=db.scalar(select(func.count()).select_from(Incident).where(Incident.status=="RESOLVED"))
    br=db.execute(select(Incident.region,func.count()).group_by(Incident.region).order_by(func.count().desc())).all()
    bs=db.execute(select(Incident.severity,func.count()).group_by(Incident.severity)).all()
    ba=db.execute(select(IncidentAgency.agency_name,func.count()).group_by(IncidentAgency.agency_name).order_by(func.count().desc())).all()
    recent=db.scalars(select(Incident).options(joinedload(Incident.reporter),joinedload(Incident.agencies)).order_by(Incident.created_at.desc()).limit(5)).unique().all()
    return {"counts":{"total":total,"pending":pending,"inProgress":progress,"resolved":resolved},
      "byRegion":[{"region":r,"_count":{"_all":c}} for r,c in br],
      "bySeverity":[{"severity":s,"_count":{"_all":c}} for s,c in bs],
      "byAgency":[{"agencyName":a,"_count":{"_all":c}} for a,c in ba],
      "recent":[serialize_incident(i) for i in recent]}

@app.post("/api/analyze-incident")
async def analyze_incident(body:AnalysisRequest, session=Depends(require_role("CITIZEN"))):
    result,source=await analyze(body.imageBase64,body.description)
    return {"analysis":result,"source":source}

@app.post("/api/upload")
async def upload(file: UploadFile=File(...), session=Depends(require_role("CITIZEN"))):
    allowed={"image/jpeg":".jpg","image/png":".png","image/webp":".webp","image/heic":".heic","image/heif":".heif"}
    ext=allowed.get((file.content_type or "").lower())
    if not ext: raise HTTPException(400,"فقط تصاویر JPG، PNG، WEBP، HEIC و HEIF مجاز هستند")
    data=await file.read()
    if len(data)>15*1024*1024: raise HTTPException(400,"حجم فایل نباید بیشتر از ۱۵ مگابایت باشد")
    filename=f"{int(datetime.utcnow().timestamp()*1000)}-{uuid4().hex}{ext}"
    path=Path(settings.upload_dir)/filename; path.write_bytes(data)
    url=f"/uploads/{filename}"
    return {"url":url}

@app.get("/api/geocode")
async def geocode(lat:float,lng:float,session=Depends(require_auth)):
    if not -90<=lat<=90 or not -180<=lng<=180: raise HTTPException(400,"مختصات نامعتبر")
    return await neshan_reverse(lat,lng)

@app.get("/api/search-location")
async def search_location(term:str,lat:float|None=None,lng:float|None=None,session=Depends(require_auth)):
    if len(term)<2: raise HTTPException(400,"عبارت جستجو حداقل ۲ کاراکتر")
    return await neshan_search(term,lat,lng)

@app.get("/api/map")
async def map_image(lat:float,lng:float,zoom:int=13,session=Depends(require_auth)):
    if not settings.neshan_api_key: raise HTTPException(503,"کلید نقشه نشان تنظیم نشده است")
    async with __import__("httpx").AsyncClient(timeout=10) as c:
        r=await c.get(map_url(lat,lng,zoom))
        if r.status_code>=400: raise HTTPException(502,"دریافت نقشه ناموفق بود")
        return RawResponse(r.content,media_type=r.headers.get("content-type","image/png"),headers={"Cache-Control":"private, max-age=300"})
