"""Repository layer.

All direct database access lives here. Repositories expose intent-revealing
data-access methods and are the only place that builds SQLAlchemy queries.
Services orchestrate them; routers never touch the database directly.
"""
from .user_repository import UserRepository
from .incident_repository import IncidentRepository
from .health_repository import ping

__all__ = ["UserRepository", "IncidentRepository", "ping"]
