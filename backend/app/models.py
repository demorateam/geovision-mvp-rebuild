from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(20), default="CITIZEN")
    agency: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    incidents: Mapped[list["Incident"]] = relationship(back_populates="reporter")

class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    incident_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    reporter_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    image_url: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(String(2000))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    region: Mapped[str] = mapped_column(String(100), default="نامشخص", index=True)
    incident_type: Mapped[str] = mapped_column(String(100), default="نامشخص")
    severity: Mapped[str] = mapped_column(String(20), default="Low", index=True)
    color_code: Mapped[str] = mapped_column(String(20), default="Green")
    ai_summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reporter: Mapped["User"] = relationship(back_populates="incidents")
    agencies: Mapped[list["IncidentAgency"]] = relationship(back_populates="incident", cascade="all, delete-orphan")
    status_history: Mapped[list["IncidentStatusHistory"]] = relationship(back_populates="incident", cascade="all, delete-orphan")

class IncidentAgency(Base):
    __tablename__ = "incident_agencies"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    agency_name: Mapped[str] = mapped_column(String(200), index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    incident: Mapped["Incident"] = relationship(back_populates="agencies")

class IncidentStatusHistory(Base):
    __tablename__ = "incident_status_history"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True)
    old_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    incident: Mapped["Incident"] = relationship(back_populates="status_history")
