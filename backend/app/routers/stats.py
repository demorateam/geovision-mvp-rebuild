from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import require_role
from ..db import get_db
from ..services.stats_service import StatsService

router = APIRouter()


@router.get("/api/stats")
def stats(session=Depends(require_role("ADMIN")), db: Session = Depends(get_db)):
    return StatsService(db).dashboard()
