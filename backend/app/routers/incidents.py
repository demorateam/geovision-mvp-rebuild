from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import require_auth, require_role
from ..db import get_db
from ..schemas import IncidentCreate, IncidentStatusUpdate
from ..services.incident_service import IncidentService

router = APIRouter()


@router.get("/api/incidents")
def list_incidents(session=Depends(require_auth), db: Session = Depends(get_db)):
    return IncidentService(db).list_incidents(session)


@router.post("/api/incidents")
def create_incident(body: IncidentCreate, session=Depends(require_role("CITIZEN")), db: Session = Depends(get_db)):
    # NOTE: the (payload, 201) tuple return is preserved on purpose:
    # FastAPI serializes it as [payload, 201] with HTTP 200, which is the
    # exact pre-refactor contract clients already depend on.
    return IncidentService(db).create_incident(body, session), 201


@router.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str, session=Depends(require_auth), db: Session = Depends(get_db)):
    return IncidentService(db).get_incident(incident_id, session)


@router.patch("/api/incidents/{incident_id}")
def update_incident(incident_id: str, body: IncidentStatusUpdate, session=Depends(require_auth), db: Session = Depends(get_db)):
    return IncidentService(db).update_status(incident_id, body, session)
