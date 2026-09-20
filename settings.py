"""Settings — export (not a restore system)."""
from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from config import BACKUPS_DIR, CONFIG
from db import (
    Attachment, DiagnosticCase, DTC, GeneratedReport, Hypothesis,
    MaintenanceRecord, Measurement, Repair, Test, TimelineEvent, Vehicle,
    session_scope,
)
from services import list_templates

username = st.session_state["username"]
st.markdown("### Settings")

st.markdown(f"**Garage name:** {CONFIG.name}")
st.markdown(f"**Subtitle:** {CONFIG.subtitle}")
st.markdown(f"**Technician:** {CONFIG.technician}")
st.markdown(f"**Case prefix:** {CONFIG.case_prefix}")
st.markdown(f"**Units:** {CONFIG.mileage_unit} · {CONFIG.temperature_unit}")
st.caption("Edit `config.py` to change branding and defaults.")

st.divider()
st.markdown("#### Export (not a restore system)")
st.caption(
    "This exports a JSON snapshot of your vehicles, cases, and child records. "
    "Attachment files and generated report PDFs are NOT included — back up "
    "`data/attachments/` and `data/reports/` separately. "
    "There is currently no import/restore path."
)

def _dump_all() -> dict:
    with session_scope() as s:
        veh = list(s.query(Vehicle).filter(Vehicle.owner == username))
        vids = [v.id for v in veh]
        cases = list(s.query(DiagnosticCase).filter(
            DiagnosticCase.vehicle_id.in_(vids))) if vids else []
        cids = [c.id for c in cases]

        def rd(table, cond):
            rows = s.query(table).filter(cond).all()
            out = []
            for r in rows:
                d = {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
                for k, v in list(d.items()):
                    if isinstance(v, datetime):
                        d[k] = v.isoformat()
                out.append(d)
            return out

        return {
            "exported_at": datetime.now().isoformat(),
            "garage": CONFIG.name,
            "vehicles": rd(Vehicle, Vehicle.owner == username),
            "cases": rd(DiagnosticCase, DiagnosticCase.vehicle_id.in_(vids)) if vids else [],
            "tests": rd(Test, Test.case_id.in_(cids)) if cids else [],
            "measurements": rd(Measurement, Measurement.case_id.in_(cids)) if cids else [],
            "dtcs": rd(DTC, DTC.case_id.in_(cids)) if cids else [],
            "hypotheses": rd(Hypothesis, Hypothesis.case_id.in_(cids)) if cids else [],
            "events": rd(TimelineEvent, TimelineEvent.case_id.in_(cids)) if cids else [],
            "repairs": rd(Repair, Repair.case_id.in_(cids)) if cids else [],
            "attachments": rd(Attachment, Attachment.case_id.in_(cids)) if cids else [],
            "reports": rd(GeneratedReport, GeneratedReport.case_id.in_(cids)) if cids else [],
            "maintenance": rd(MaintenanceRecord, MaintenanceRecord.vehicle_id.in_(vids)) if vids else [],
        }

if st.button("Build JSON export", type="primary"):
    data = _dump_all()
    BACKUPS_DIR.mkdir(exist_ok=True)
    p = BACKUPS_DIR / f"export_{datetime.now():%Y%m%d_%H%M%S}.json"
    p.write_text(json.dumps(data, indent=2, default=str))
    st.success(f"Exported: {p.name}")
    st.download_button("⬇  Download JSON", data=p.read_text(),
                       file_name=p.name, mime="application/json")

st.divider()
st.markdown("#### Report templates")
templates = list_templates(username)
if not templates:
    st.caption("No saved templates yet. Built-in templates are always available.")
else:
    for t in templates:
        st.markdown(f"**{t.name}** ({t.audience}) — {len(t.sections)} sections")

st.divider()
st.caption(f"{CONFIG.name} — {CONFIG.subtitle} · Document version {CONFIG.doc_version}")
