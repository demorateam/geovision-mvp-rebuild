"""One-time migration helper from the old Prisma/SQLite database to PostgreSQL.
Usage inside backend container after copying the old dev.db:
  python -m app.migrate_sqlite /app/legacy/dev.db
"""
import sqlite3, sys
from datetime import datetime
from .db import Base, SessionLocal, engine
from .models import User, Incident, IncidentAgency, IncidentStatusHistory

def val(row, key): return row[key] if key in row.keys() else None

def main(path):
    Base.metadata.create_all(engine)
    src=sqlite3.connect(path); src.row_factory=sqlite3.Row
    db=SessionLocal()
    try:
        for r in src.execute("SELECT * FROM User"):
            db.merge(User(id=r["id"],name=r["name"],phone=r["phone"],role=r["role"],agency=r["agency"],created_at=r["createdAt"].replace("Z","") if isinstance(r["createdAt"],str) else datetime.utcnow()))
        db.commit()
        for r in src.execute("SELECT * FROM Incident"):
            db.merge(Incident(id=r["id"],incident_number=r["incidentNumber"],reporter_id=r["reporterId"],image_url=r["imageUrl"],description=r["description"],latitude=r["latitude"],longitude=r["longitude"],region=r["region"],incident_type=r["incidentType"],severity=r["severity"],color_code=r["colorCode"],ai_summary=r["aiSummary"],status=r["status"],created_at=r["createdAt"].replace("Z","") if isinstance(r["createdAt"],str) else datetime.utcnow(),updated_at=r["updatedAt"].replace("Z","") if isinstance(r["updatedAt"],str) else datetime.utcnow()))
        db.commit()
        for r in src.execute("SELECT * FROM IncidentAgency"):
            db.merge(IncidentAgency(id=r["id"],incident_id=r["incidentId"],agency_name=r["agencyName"],assigned_at=r["assignedAt"].replace("Z","") if isinstance(r["assignedAt"],str) else datetime.utcnow()))
        for r in src.execute("SELECT * FROM IncidentStatusHistory"):
            db.merge(IncidentStatusHistory(id=r["id"],incident_id=r["incidentId"],old_status=r["oldStatus"],new_status=r["newStatus"],created_at=r["createdAt"].replace("Z","") if isinstance(r["createdAt"],str) else datetime.utcnow()))
        db.commit()
        print("SQLite migration completed.")
    finally:
        db.close(); src.close()
if __name__=="__main__":
    main(sys.argv[1])
