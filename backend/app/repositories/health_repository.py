from sqlalchemy import text
from sqlalchemy.orm import Session


def ping(db: Session) -> None:
    """Database connectivity probe used by the health endpoint."""
    db.execute(text("SELECT 1"))
