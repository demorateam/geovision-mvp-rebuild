from sqlalchemy.orm import Session

from ..repositories import IncidentRepository
from ..serializers import incident as serialize_incident


class StatsService:
    """Admin dashboard aggregations."""

    def __init__(self, db: Session):
        self.incidents = IncidentRepository(db)

    def dashboard(self):
        total = self.incidents.count_total()
        pending = self.incidents.count_by_status("PENDING")
        progress = self.incidents.count_by_status("IN_PROGRESS")
        resolved = self.incidents.count_by_status("RESOLVED")
        by_region = self.incidents.count_by_region()
        by_severity = self.incidents.count_by_severity()
        by_agency = self.incidents.count_by_agency()
        recent = self.incidents.list_recent(5)
        return {
            "counts": {"total": total, "pending": pending, "inProgress": progress, "resolved": resolved},
            "byRegion": [{"region": r, "_count": {"_all": c}} for r, c in by_region],
            "bySeverity": [{"severity": s, "_count": {"_all": c}} for s, c in by_severity],
            "byAgency": [{"agencyName": a, "_count": {"_all": c}} for a, c in by_agency],
            "recent": [serialize_incident(i) for i in recent],
        }
