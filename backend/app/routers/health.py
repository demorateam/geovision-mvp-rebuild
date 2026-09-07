from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..repositories import ping

router = APIRouter()


@router.get("/api/health")
def health(db: Session = Depends(get_db)):
    try:
        ping(db)
    except Exception:
        raise HTTPException(503, {"status": "error", "database": "unavailable"})
    return {"status": "ok", "database": "connected", "timestamp": datetime.utcnow().isoformat() + "Z"}
