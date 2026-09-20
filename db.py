"""Suraj's Garage — SQLAlchemy models, engine, and session management."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator

from sqlalchemy import (
    JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text,
    create_engine, event,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker,
)

from config import DB_PATH


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    """Local wall-clock time (naive). Existing rows stay as stored."""
    return datetime.now()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now
    )


# ── Vehicles ───────────────────────────────────────────────────────────────
class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(64), index=True)
    nickname: Mapped[str] = mapped_column(String(120))
    year: Mapped[int | None] = mapped_column(Integer)
    make: Mapped[str | None] = mapped_column(String(80))
    model: Mapped[str | None] = mapped_column(String(80))
    trim: Mapped[str | None] = mapped_column(String(80))
    vin: Mapped[str | None] = mapped_column(String(32), index=True)
    engine: Mapped[str | None] = mapped_column(String(120))
    engine_code: Mapped[str | None] = mapped_column(String(40))
    transmission: Mapped[str | None] = mapped_column(String(80))
    drivetrain: Mapped[str | None] = mapped_column(String(20))
    plate: Mapped[str | None] = mapped_column(String(40))
    mileage: Mapped[int | None] = mapped_column(Integer)
    owner_name: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    mods: Mapped[list | None] = mapped_column(JSON)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)

    cases: Mapped[list["DiagnosticCase"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan", lazy="selectin"
    )
    maintenance: Mapped[list["MaintenanceRecord"]] = relationship(
        back_populates="vehicle", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def title(self) -> str:
        bits = [str(self.year or ""), self.make or "", self.model or ""]
        return " ".join(b for b in bits if b).strip() or self.nickname


# ── Cases ──────────────────────────────────────────────────────────────────
class DiagnosticCase(TimestampMixin, Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32), default="open")
    classification: Mapped[str | None] = mapped_column(String(40))
    tags: Mapped[list | None] = mapped_column(JSON)

    # Narrative sections stored as JSON (schema-driven, migration-free)
    complaint: Mapped[dict | None] = mapped_column(JSON)
    initial_condition: Mapped[dict | None] = mapped_column(JSON)
    scan_data: Mapped[dict | None] = mapped_column(JSON)
    symptoms: Mapped[dict | None] = mapped_column(JSON)
    plan: Mapped[dict | None] = mapped_column(JSON)
    wiring: Mapped[dict | None] = mapped_column(JSON)
    root_cause: Mapped[dict | None] = mapped_column(JSON)
    repair_notes: Mapped[dict | None] = mapped_column(JSON)
    verification: Mapped[dict | None] = mapped_column(JSON)
    remaining: Mapped[dict | None] = mapped_column(JSON)
    safety: Mapped[dict | None] = mapped_column(JSON)
    maintenance_obs: Mapped[dict | None] = mapped_column(JSON)
    summary: Mapped[dict | None] = mapped_column(JSON)
    reflection: Mapped[dict | None] = mapped_column(JSON)
    costs: Mapped[dict | None] = mapped_column(JSON)
    final_status: Mapped[dict | None] = mapped_column(JSON)

    opened_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="cases", lazy="joined")
    tests: Mapped[list["Test"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    dtcs: Mapped[list["DTC"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    hypotheses: Mapped[list["Hypothesis"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    events: Mapped[list["TimelineEvent"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    repairs: Mapped[list["Repair"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )
    reports: Mapped[list["GeneratedReport"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", lazy="selectin"
    )


class Test(TimestampMixin, Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    system: Mapped[str | None] = mapped_column(String(80))
    component: Mapped[str | None] = mapped_column(String(200))
    procedure: Mapped[str] = mapped_column(Text)
    tool: Mapped[str | None] = mapped_column(String(120))
    conditions: Mapped[str | None] = mapped_column(Text)
    expected: Mapped[str | None] = mapped_column(String(200))
    actual: Mapped[str | None] = mapped_column(String(200))
    result: Mapped[str] = mapped_column(String(16), default="inconclusive")
    interpretation: Mapped[str | None] = mapped_column(Text)
    proves: Mapped[str | None] = mapped_column(Text)
    rules_out: Mapped[str | None] = mapped_column(Text)
    next_step: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="tests")


class Measurement(TimestampMixin, Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    system: Mapped[str | None] = mapped_column(String(80))
    component: Mapped[str | None] = mapped_column(String(160))
    value_type: Mapped[str] = mapped_column(String(16), default="numeric")
    value_num: Mapped[float | None] = mapped_column(Float)
    value_text: Mapped[str | None] = mapped_column(String(200))
    units: Mapped[str | None] = mapped_column(String(32))
    spec_min: Mapped[float | None] = mapped_column(Float)
    spec_max: Mapped[float | None] = mapped_column(Float)
    spec_text: Mapped[str | None] = mapped_column(String(200))
    spec_source: Mapped[str | None] = mapped_column(String(200))
    conditions: Mapped[str | None] = mapped_column(Text)
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="measurements")

    @property
    def in_spec(self) -> bool | None:
        if self.value_num is None:
            return None
        if self.spec_min is None and self.spec_max is None:
            return None
        if self.spec_min is not None and self.value_num < self.spec_min:
            return False
        if self.spec_max is not None and self.value_num > self.spec_max:
            return False
        return True


class DTC(TimestampMixin, Base):
    __tablename__ = "dtcs"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    code: Mapped[str] = mapped_column(String(16), index=True)
    module: Mapped[str | None] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(32), default="present")
    freeze_frame: Mapped[str | None] = mapped_column(Text)
    associated_symptoms: Mapped[str | None] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    returned_after_repair: Mapped[bool] = mapped_column(Boolean, default=False)
    first_seen: Mapped[datetime] = mapped_column(DateTime, default=_now)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=_now)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="dtcs")


class Hypothesis(TimestampMixin, Base):
    __tablename__ = "hypotheses"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    label: Mapped[str] = mapped_column(String(40))
    statement: Mapped[str] = mapped_column(Text)
    supporting: Mapped[str | None] = mapped_column(Text)
    contradicting: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="suspected")
    confidence: Mapped[int] = mapped_column(Integer, default=50)
    disposition: Mapped[str | None] = mapped_column(Text)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="hypotheses")


class TimelineEvent(TimestampMixin, Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    kind: Mapped[str] = mapped_column(String(48), default="note")
    description: Mapped[str] = mapped_column(Text)
    decision: Mapped[str | None] = mapped_column(Text)
    next_action: Mapped[str | None] = mapped_column(Text)
    auto: Mapped[bool] = mapped_column(Boolean, default=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, index=True
    )

    case: Mapped["DiagnosticCase"] = relationship(back_populates="events")


class Repair(TimestampMixin, Base):
    __tablename__ = "repairs"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    parts: Mapped[str | None] = mapped_column(Text)
    part_numbers: Mapped[str | None] = mapped_column(Text)
    fluids: Mapped[str | None] = mapped_column(Text)
    wiring_repair: Mapped[str | None] = mapped_column(Text)
    calibration: Mapped[str | None] = mapped_column(Text)
    torque: Mapped[str | None] = mapped_column(Text)
    labor_time: Mapped[float | None] = mapped_column(Float)
    cost: Mapped[float | None] = mapped_column(Float)
    why: Mapped[str | None] = mapped_column(Text)
    performed_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="repairs")


class MaintenanceRecord(TimestampMixin, Base):
    __tablename__ = "maintenance"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), index=True)
    kind: Mapped[str] = mapped_column(String(120))
    due_mileage: Mapped[int | None] = mapped_column(Integer)
    due_date: Mapped[datetime | None] = mapped_column(DateTime)
    done_at: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)

    vehicle: Mapped["Vehicle"] = relationship(back_populates="maintenance")


class Attachment(TimestampMixin, Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    test_id: Mapped[int | None] = mapped_column(ForeignKey("tests.id"), nullable=True)
    kind: Mapped[str] = mapped_column(String(32), default="photo")
    category: Mapped[str | None] = mapped_column(String(40))
    filename: Mapped[str] = mapped_column(String(240))
    stored_name: Mapped[str] = mapped_column(String(240))
    mime: Mapped[str | None] = mapped_column(String(80))
    size: Mapped[int | None] = mapped_column(Integer)
    caption: Mapped[str | None] = mapped_column(String(400))
    notes: Mapped[str | None] = mapped_column(Text)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="attachments")


class ReportTemplate(TimestampMixin, Base):
    __tablename__ = "report_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(120))
    audience: Mapped[str] = mapped_column(String(32), default="internal")
    sections: Mapped[list] = mapped_column(JSON)
    options: Mapped[dict | None] = mapped_column(JSON)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)


class GeneratedReport(TimestampMixin, Base):
    __tablename__ = "generated_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    report_type: Mapped[str] = mapped_column(String(32), default="internal")
    template_name: Mapped[str | None] = mapped_column(String(120))
    version: Mapped[int] = mapped_column(Integer, default=1)
    sections: Mapped[list] = mapped_column(JSON)
    html: Mapped[str | None] = mapped_column(Text)
    file_path: Mapped[str | None] = mapped_column(String(400))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)

    case: Mapped["DiagnosticCase"] = relationship(back_populates="reports")


# ── Engine & Session ───────────────────────────────────────────────────────
ENGINE = create_engine(
    f"sqlite:///{DB_PATH}",
    future=True,
    connect_args={"check_same_thread": False},
)

# Enable foreign keys for SQLite
@event.listens_for(ENGINE, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=ENGINE, expire_on_commit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(ENGINE)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
