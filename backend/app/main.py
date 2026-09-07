"""Application assembly.

Wires the FastAPI app together: exception handlers, CORS, static uploads,
startup hook and route registration. All endpoint handlers live in
app.routers.*, business logic in app.services.*, database access in
app.repositories.*.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException as FastAPIHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import Base, engine
from .routers import ai, auth, geo, health, incidents, stats, uploads

app=FastAPI(title="UEMP Backend", version="1.0.0")

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

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(incidents.router)
app.include_router(stats.router)
app.include_router(ai.router)
app.include_router(uploads.router)
app.include_router(geo.router)
