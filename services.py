"""All CRUD operations — the only place that touches the DB."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, or_, func

from config import CONFIG
from db import (
    Attachment, DiagnosticCase, DTC, GeneratedReport, Hypothesis,
    MaintenanceRecord, Measurement, Repair, ReportTemplate, Test,
    TimelineEvent, Vehicle, session_scope,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------ ids
def next_case_number(owner: str) -> str:
    today = _now().strftime("%Y%m%d")
    prefix = f"{CONFIG.case_prefix}-{today}-"
    with session_scope() as s:
        n = s.scalar(
            select(func.count()).select_from(DiagnosticCase)
            .where(DiagnosticCase.case_number.like(prefix + "%"))
        )
    return f"{prefix}{(n or 0) + 1:03d}"


# ------------------------------------------------------------------ vehicles
def list_vehicles(owner: str, include_archived: bool = False) -> list[Vehicle]:
    with session_scope() as s:
        q = select(Vehicle).where(Vehicle.owner == owner)
        if not include_archived:
            q = q.where(Vehicle.archived == False)  # noqa: E712
        return list(s.scalars(q.order_by(Vehicle.created_at.desc())))


def get_vehicle(vehicle_id: int) -> Vehicle | None:
    with session_scope() as s:
        return s.get(Vehicle, vehicle_id)


def create_vehicle(owner: str, data: dict) -> int:
    with session_scope() as s:
        v = Vehicle(owner=owner, **data)
        s.add(v)
        s.flush()
        return v.id


def update_vehicle(vehicle_id: int, data: dict) -> None:
    with session_scope() as s:
        v = s.get(Vehicle, vehicle_id)
        if not v:
            return
        for k, val in data.items():
            setattr(v, k, val)


def archive_vehicle(vehicle_id: int, archived: bool = True) -> None:
    with session_scope() as s:
        v = s.get(Vehicle, vehicle_id)
        if v:
            v.archived = archived


def delete_vehicle(vehicle_id: int) -> None:
    with session_scope() as s:
        v = s.get(Vehicle, vehicle_id)
        if v:
            s.delete(v)


# ------------------------------------------------------------------ cases
def list_cases(owner: str, vehicle_id: int | None = None,
               status: str | None = None) -> list[DiagnosticCase]:
    with session_scope() as s:
        q = select(DiagnosticCase).join(Vehicle).where(Vehicle.owner == owner)
        if vehicle_id:
            q = q.where(DiagnosticCase.vehicle_id == vehicle_id)
        if status:
            q = q.where(DiagnosticCase.status == status)
        return list(s.scalars(q.order_by(DiagnosticCase.opened_at.desc())))


def get_case(case_id: int) -> DiagnosticCase | None:
    with session_scope() as s:
        return s.get(DiagnosticCase, case_id)


def create_case(owner: str, vehicle_id: int, title: str,
                classification: str | None = None) -> int:
    case_number = next_case_number(owner)
    with session_scope() as s:
        c = DiagnosticCase(
            case_number=case_number, vehicle_id=vehicle_id, title=title,
            status="open", classification=classification,
        )
        s.add(c)
        s.flush()
        s.add(TimelineEvent(case_id=c.id, kind="case",
                            description=f"Case opened: {title}", auto=True))
        return c.id


def update_case_section(case_id: int, attr: str, values: dict) -> None:
    with session_scope() as s:
        c = s.get(DiagnosticCase, case_id)
        if not c:
            return
        setattr(c, attr, values)
        s.add(TimelineEvent(case_id=case_id, kind="section",
                            description=f"Updated {attr.replace('_', ' ')}", auto=True))


def update_case_meta(case_id: int, **fields: Any) -> None:
    with session_scope() as s:
        c = s.get(DiagnosticCase, case_id)
        if not c:
            return
        for k, v in fields.items():
            setattr(c, k, v)


def delete_case(case_id: int) -> None:
    with session_scope() as s:
        c = s.get(DiagnosticCase, case_id)
        if c:
            s.delete(c)


# ------------------------------------------------------------------ tests
def list_tests(case_id: int) -> list[Test]:
    with session_scope() as s:
        return list(s.scalars(
            select(Test).where(Test.case_id == case_id).order_by(Test.id)
        ))


def create_test(case_id: int, data: dict) -> int:
    with session_scope() as s:
        t = Test(case_id=case_id, **data)
        s.add(t)
        s.flush()
        s.add(TimelineEvent(case_id=case_id, kind="test",
                            description=f"Test: {data.get('procedure', '')[:120]}",
                            auto=True))
        return t.id


def update_test(test_id: int, data: dict) -> None:
    with session_scope() as s:
        t = s.get(Test, test_id)
        if t:
            for k, v in data.items():
                setattr(t, k, v)


def delete_test(test_id: int) -> None:
    with session_scope() as s:
        t = s.get(Test, test_id)
        if t:
            s.delete(t)


# ------------------------------------------------------------------ measurements
def list_measurements(case_id: int) -> list[Measurement]:
    with session_scope() as s:
        return list(s.scalars(
            select(Measurement).where(Measurement.case_id == case_id)
            .order_by(Measurement.id)
        ))


def create_measurement(case_id: int, data: dict) -> int:
    with session_scope() as s:
        m = Measurement(case_id=case_id, **data)
        s.add(m)
        s.flush()
        s.add(TimelineEvent(case_id=case_id, kind="measurement",
                            description=f"Measurement: {data.get('name', '')}", auto=True))
        return m.id


def delete_measurement(mid: int) -> None:
    with session_scope() as s:
        m = s.get(Measurement, mid)
        if m:
            s.delete(m)


# ------------------------------------------------------------------ dtcs
def list_dtcs(case_id: int) -> list[DTC]:
    with session_scope() as s:
        return list(s.scalars(
            select(DTC).where(DTC.case_id == case_id).order_by(DTC.code)
        ))


def create_dtc(case_id: int, data: dict) -> int:
    with session_scope() as s:
        d = DTC(case_id=case_id, **data)
        s.add(d)
        s.flush()
        s.add(TimelineEvent(case_id=case_id, kind="dtc",
                            description=f"DTC recorded: {data.get('code', '')}", auto=True))
        return d.id


def delete_dtc(did: int) -> None:
    with session_scope() as s:
        d = s.get(DTC, did)
        if d:
            s.delete(d)


# ------------------------------------------------------------------ hypotheses
def list_hypotheses(case_id: int) -> list[Hypothesis]:
    with session_scope() as s:
        return list(s.scalars(
            select(Hypothesis).where(Hypothesis.case_id == case_id)
            .order_by(Hypothesis.id)
        ))


def create_hypothesis(case_id: int, data: dict) -> int:
    with session_scope() as s:
        n = s.scalar(
            select(func.count()).select_from(Hypothesis)
            .where(Hypothesis.case_id == case_id)
        ) or 0
        data.setdefault("label", f"H{n + 1}")
        h = Hypothesis(case_id=case_id, **data)
        s.add(h)
        s.flush()
        s.add(TimelineEvent(case_id=case_id, kind="hypothesis",
                            description=f"Hypothesis {h.label}: {data.get('statement', '')[:80]}",
                            auto=True))
        return h.id


def update_hypothesis(hid: int, data: dict) -> None:
    with session_scope() as s:
        h = s.get(Hypothesis, hid)
        if h:
            for k, v in data.items():
                setattr(h, k, v)


def delete_hypothesis(hid: int) -> None:
    with session_scope() as s:
        h = s.get(Hypothesis, hid)
        if h:
            s.delete(h)


# ------------------------------------------------------------------ events
def list_events(case_id: int) -> list[TimelineEvent]:
    with session_scope() as s:
        return list(s.scalars(
            select(TimelineEvent).where(TimelineEvent.case_id == case_id)
            .order_by(TimelineEvent.occurred_at)
        ))


def create_event(case_id: int, description: str, kind: str = "note",
                 decision: str | None = None, next_action: str | None = None,
                 occurred_at: datetime | None = None) -> int:
    with session_scope() as s:
        e = TimelineEvent(
            case_id=case_id, description=description, kind=kind,
            decision=decision, next_action=next_action,
            occurred_at=occurred_at or _now(),
        )
        s.add(e)
        s.flush()
        return e.id


def delete_event(eid: int) -> None:
    with session_scope() as s:
        e = s.get(TimelineEvent, eid)
        if e and not e.auto:
            s.delete(e)


# ------------------------------------------------------------------ repairs
def list_repairs(case_id: int) -> list[Repair]:
    with session_scope() as s:
        return list(s.scalars(
            select(Repair).where(Repair.case_id == case_id).order_by(Repair.id)
        ))


def create_repair(case_id: int, data: dict) -> int:
    with session_scope() as s:
        r = Repair(case_id=case_id, **data)
        s.add(r)
        s.flush()
        s.add(TimelineEvent(case_id=case_id, kind="repair",
                            description=f"Repair: {data.get('description', '')[:120]}",
                            auto=True))
        return r.id


def delete_repair(rid: int) -> None:
    with session_scope() as s:
        r = s.get(Repair, rid)
        if r:
            s.delete(r)


# ------------------------------------------------------------------ maintenance
def list_maintenance(vehicle_id: int) -> list[MaintenanceRecord]:
    with session_scope() as s:
        return list(s.scalars(
            select(MaintenanceRecord).where(MaintenanceRecord.vehicle_id == vehicle_id)
            .order_by(MaintenanceRecord.created_at.desc())
        ))


def create_maintenance(vehicle_id: int, data: dict) -> int:
    with session_scope() as s:
        m = MaintenanceRecord(vehicle_id=vehicle_id, **data)
        s.add(m)
        s.flush()
        return m.id


# ------------------------------------------------------------------ attachments
def list_attachments(case_id: int) -> list[Attachment]:
    with session_scope() as s:
        return list(s.scalars(
            select(Attachment).where(Attachment.case_id == case_id)
            .order_by(Attachment.id.desc())
        ))


def create_attachment(case_id: int, data: dict) -> int:
    with session_scope() as s:
        a = Attachment(case_id=case_id, **data)
        s.add(a)
        s.flush()
        s.add(TimelineEvent(case_id=case_id, kind="attachment",
                            description=f"Attachment: {data.get('caption') or data.get('filename','')}",
                            auto=True))
        return a.id


def delete_attachment(aid: int) -> None:
    with session_scope() as s:
        a = s.get(Attachment, aid)
        if a:
            s.delete(a)


# ------------------------------------------------------------------ templates
def list_templates(owner: str) -> list[ReportTemplate]:
    with session_scope() as s:
        return list(s.scalars(
            select(ReportTemplate).where(ReportTemplate.owner == owner)
            .order_by(ReportTemplate.is_builtin.desc(), ReportTemplate.name)
        ))


def create_template(owner: str, name: str, audience: str,
                    sections: list, options: dict | None = None) -> int:
    with session_scope() as s:
        t = ReportTemplate(owner=owner, name=name, audience=audience,
                           sections=sections, options=options or {})
        s.add(t)
        s.flush()
        return t.id


# ------------------------------------------------------------------ reports
def list_reports(case_id: int) -> list[GeneratedReport]:
    with session_scope() as s:
        return list(s.scalars(
            select(GeneratedReport).where(GeneratedReport.case_id == case_id)
            .order_by(GeneratedReport.created_at.desc())
        ))


def save_report(case_id: int, name: str, report_type: str,
                template_name: str | None, sections: list,
                html: str | None, file_path: str | None,
                metadata: dict | None = None) -> int:
    with session_scope() as s:
        version = (s.scalar(
            select(func.count()).select_from(GeneratedReport)
            .where(GeneratedReport.case_id == case_id)
        ) or 0) + 1
        r = GeneratedReport(
            case_id=case_id, name=name, report_type=report_type,
            template_name=template_name, version=version,
            sections=sections, html=html, file_path=file_path,
            metadata_json=metadata or {},
        )
        s.add(r)
        s.flush()
        return r.id


# ------------------------------------------------------------------ search
def global_search(owner: str, query: str, limit: int = 80) -> dict:
    q = f"%{query.lower()}%"
    results: dict = {"vehicles": [], "cases": [], "tests": [], "dtcs": [],
                     "measurements": [], "repairs": [], "events": []}
    if not query.strip():
        return results
    with session_scope() as s:
        veh_ids = [v.id for v in s.scalars(select(Vehicle).where(Vehicle.owner == owner))]

        results["vehicles"] = list(s.scalars(
            select(Vehicle).where(
                Vehicle.owner == owner,
                or_(
                    func.lower(Vehicle.nickname).like(q),
                    func.lower(Vehicle.vin).like(q),
                    func.lower(Vehicle.make).like(q),
                    func.lower(Vehicle.model).like(q),
                ),
            ).limit(limit)
        ))

        case_ids = [c.id for c in s.scalars(
            select(DiagnosticCase).where(DiagnosticCase.vehicle_id.in_(veh_ids))
        )] if veh_ids else []

        if case_ids:
            results["cases"] = list(s.scalars(
                select(DiagnosticCase).where(
                    DiagnosticCase.id.in_(case_ids),
                    or_(
                        func.lower(DiagnosticCase.case_number).like(q),
                        func.lower(DiagnosticCase.title).like(q),
                    ),
                ).limit(limit)
            ))
            results["tests"] = list(s.scalars(
                select(Test).where(
                    Test.case_id.in_(case_ids),
                    or_(
                        func.lower(Test.procedure).like(q),
                        func.lower(Test.component).like(q),
                    ),
                ).limit(limit)
            ))
            results["dtcs"] = list(s.scalars(
                select(DTC).where(
                    DTC.case_id.in_(case_ids),
                    func.lower(DTC.code).like(q),
                ).limit(limit)
            ))
            results["measurements"] = list(s.scalars(
                select(Measurement).where(
                    Measurement.case_id.in_(case_ids),
                    func.lower(Measurement.name).like(q),
                ).limit(limit)
            ))
            results["repairs"] = list(s.scalars(
                select(Repair).where(
                    Repair.case_id.in_(case_ids),
                    func.lower(Repair.description).like(q),
                ).limit(limit)
            ))
            results["events"] = list(s.scalars(
                select(TimelineEvent).where(
                    TimelineEvent.case_id.in_(case_ids),
                    func.lower(TimelineEvent.description).like(q),
                ).limit(limit)
            ))
    return results
