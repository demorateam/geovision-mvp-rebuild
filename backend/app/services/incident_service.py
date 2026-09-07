import random
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Incident
from ..repositories import IncidentRepository
from ..schemas import IncidentCreate, IncidentStatusUpdate
from ..serializers import incident as serialize_incident


class IncidentService:
    """Incident business rules: visibility scoping, access checks, incident
    number generation and status transitions."""

    def __init__(self, db: Session):
        self.incidents = IncidentRepository(db)

    @staticmethod
    def _can_view(session, incident: Incident) -> bool:
        return (
            session["role"] == "ADMIN"
            or (session["role"] == "CITIZEN" and incident.reporter_id == session["id"])
            or (session["role"] == "AGENCY" and any(a.agency_name == session.get("agency") for a in incident.agencies))
        )

    @staticmethod
    def _can_manage(session, incident: Incident) -> bool:
        return (
            session["role"] == "ADMIN"
            or (session["role"] == "AGENCY" and any(a.agency_name == session.get("agency") for a in incident.agencies))
        )

    def list_incidents(self, session):
        if session["role"] == "CITIZEN":
            items = self.incidents.list_by_reporter(session["id"])
        elif session["role"] == "AGENCY":
            items = self.incidents.list_by_agency(session.get("agency", ""))
        else:
            items = self.incidents.list_all()
        return {"incidents": [serialize_incident(i) for i in items]}

    def get_incident(self, incident_id: str, session):
        i = self.incidents.get_detail(incident_id)
        if not i:
            raise HTTPException(404, "رخداد یافت نشد")
        if not self._can_view(session, i):
            raise HTTPException(403, "دسترسی مجاز نیست")
        return {"incident": serialize_incident(i, include_history=True)}

    def create_incident(self, body: IncidentCreate, session):
        datepart = datetime.utcnow().strftime("%y%m%d")
        incident_number = f"INC-{datepart}-{random.randint(100000, 999999)}"
        while self.incidents.incident_number_exists(incident_number):
            incident_number = f"INC-{datepart}-{random.randint(100000, 999999)}"
        i = Incident(
            id=uuid4().hex, incident_number=incident_number, reporter_id=session["id"],
            image_url=body.imageUrl, description=body.description,
            latitude=body.latitude, longitude=body.longitude,
            region=body.region or "نامشخص", incident_type=body.incidentType or "نامشخص",
            severity=body.severity or "Medium", color_code=body.colorCode or "Yellow",
            ai_summary=body.aiSummary, status="PENDING",
        )
        i = self.incidents.create_with_agencies(i, body.assignedAgencies or [])
        return {"incident": serialize_incident(i)}

    def update_status(self, incident_id: str, body: IncidentStatusUpdate, session):
        i = self.incidents.get_with_agencies_and_reporter(incident_id)
        if not i:
            raise HTTPException(404, "رخداد یافت نشد")
        if not self._can_manage(session, i):
            raise HTTPException(403, "دسترسی مجاز نیست")
        old = i.status
        new = body.status or old
        i = self.incidents.apply_status_change(i, old, new)
        return {"incident": serialize_incident(i)}
