from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..models import Incident, IncidentAgency, IncidentStatusHistory


class IncidentRepository:
    """Data access for Incident aggregates (incidents, agency assignments,
    status history) and for the admin dashboard aggregations."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    # Queries
    # ------------------------------------------------------------------ #

    def list_all(self) -> list[Incident]:
        q = (
            select(Incident)
            .options(joinedload(Incident.reporter), joinedload(Incident.agencies))
            .order_by(Incident.created_at.desc())
        )
        return self.db.scalars(q).unique().all()

    def list_by_reporter(self, reporter_id: str) -> list[Incident]:
        q = (
            select(Incident)
            .options(joinedload(Incident.reporter), joinedload(Incident.agencies))
            .order_by(Incident.created_at.desc())
            .where(Incident.reporter_id == reporter_id)
        )
        return self.db.scalars(q).unique().all()

    def list_by_agency(self, agency_name: str) -> list[Incident]:
        q = (
            select(Incident)
            .options(joinedload(Incident.reporter), joinedload(Incident.agencies))
            .order_by(Incident.created_at.desc())
            .join(IncidentAgency)
            .where(IncidentAgency.agency_name == agency_name)
        )
        return self.db.scalars(q).unique().all()

    def get_detail(self, incident_id: str) -> Incident | None:
        q = (
            select(Incident)
            .options(
                joinedload(Incident.reporter),
                joinedload(Incident.agencies),
                joinedload(Incident.status_history),
            )
            .where(Incident.id == incident_id)
        )
        return self.db.execute(q).unique().scalar_one_or_none()

    def get_with_agencies_and_reporter(self, incident_id: str) -> Incident | None:
        q = (
            select(Incident)
            .options(joinedload(Incident.agencies), joinedload(Incident.reporter))
            .where(Incident.id == incident_id)
        )
        return self.db.execute(q).unique().scalar_one_or_none()

    def reload_with_agencies_and_reporter(self, incident: Incident) -> Incident:
        """Re-select an incident right after commit, with eager-loaded relations."""
        q = (
            select(Incident)
            .options(joinedload(Incident.agencies), joinedload(Incident.reporter))
            .where(Incident.id == incident.id)
        )
        return self.db.execute(q).unique().scalar_one()

    def incident_number_exists(self, incident_number: str) -> bool:
        return (
            self.db.scalar(select(Incident).where(Incident.incident_number == incident_number))
            is not None
        )

    def list_recent(self, limit: int = 5) -> list[Incident]:
        q = (
            select(Incident)
            .options(joinedload(Incident.reporter), joinedload(Incident.agencies))
            .order_by(Incident.created_at.desc())
            .limit(limit)
        )
        return self.db.scalars(q).unique().all()

    # ------------------------------------------------------------------ #
    # Aggregations (admin dashboard stats)
    # ------------------------------------------------------------------ #

    def count_total(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Incident))

    def count_by_status(self, status: str) -> int:
        return self.db.scalar(select(func.count()).select_from(Incident).where(Incident.status == status))

    def count_by_region(self):
        return self.db.execute(
            select(Incident.region, func.count()).group_by(Incident.region).order_by(func.count().desc())
        ).all()

    def count_by_severity(self):
        return self.db.execute(
            select(Incident.severity, func.count()).group_by(Incident.severity)
        ).all()

    def count_by_agency(self):
        return self.db.execute(
            select(IncidentAgency.agency_name, func.count())
            .group_by(IncidentAgency.agency_name)
            .order_by(func.count().desc())
        ).all()

    # ------------------------------------------------------------------ #
    # Writes
    # ------------------------------------------------------------------ #

    def create_with_agencies(self, incident: Incident, agency_names: list[str]) -> Incident:
        """Persists the incident, its agency assignments and the initial
        status history entry in one commit, then returns it fully loaded."""
        self.db.add(incident)
        for a in agency_names:
            self.db.add(IncidentAgency(id=uuid4().hex, incident_id=incident.id, agency_name=a))
        self.db.add(IncidentStatusHistory(id=uuid4().hex, incident_id=incident.id, new_status="PENDING"))
        self.db.commit()
        self.db.refresh(incident)
        return self.reload_with_agencies_and_reporter(incident)

    def apply_status_change(self, incident: Incident, old_status: str, new_status: str) -> Incident:
        """Applies a status transition, recording history when it actually changed."""
        incident.status = new_status
        if old_status != new_status:
            self.db.add(
                IncidentStatusHistory(
                    id=uuid4().hex, incident_id=incident.id, old_status=old_status, new_status=new_status
                )
            )
        self.db.commit()
        self.db.refresh(incident)
        return incident
