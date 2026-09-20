"""Case workspace — the heart of the app.

Tabbed sections, quick actions, structured records (tests, measurements,
DTCs, hypotheses, timeline, repairs, attachments).
"""
from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from config import CONFIG
from form_renderer import render_section_form
from schemas import (
    NARRATIVE_SECTIONS, SECTION_TO_ATTR, VEHICLE_SYSTEMS, TEST_RESULTS,
    DTC_STATUSES, HYPOTHESIS_STATUSES,
)
from services import (
    create_attachment, create_dtc, create_event, create_hypothesis,
    create_measurement, create_repair, create_test, delete_attachment,
    delete_dtc, delete_event, delete_hypothesis, delete_measurement,
    delete_repair, delete_test, get_case, list_attachments, list_dtcs,
    list_events, list_hypotheses, list_measurements, list_repairs,
    list_tests, update_case_section, update_case_meta,
)
from storage import attachment_path, save_upload

case_id = st.session_state.get("current_case_id")
if not case_id:
    st.warning("Open a case from the Cases page.")
    st.stop()

case = get_case(case_id)
if not case:
    st.error("Case not found.")
    st.stop()

# ------------------------------------------------------------------ header
v = case.vehicle
h1, h2 = st.columns([4, 1])
with h1:
    st.markdown(f"## {CONFIG.name}")
    st.markdown(f"### {case.title}")
    if v.mileage:
        st.caption(f"{case.case_number}  ·  {v.title}  ·  VIN {v.vin or '—'}  ·  "
                   f"{v.mileage:,} {CONFIG.mileage_unit}")
    else:
        st.caption(f"{case.case_number}  ·  {v.title}  ·  VIN {v.vin or '—'}")
with h2:
    if st.button("← All cases", use_container_width=True):
        st.session_state.pop("current_case_id", None)
        st.session_state["nav"] = "Cases"
        st.rerun()
    st.caption(f"Status: **{case.status}**")

# ------------------------------------------------------------------ quick actions
st.write("")
st.markdown("##### Quick actions")
qa = st.columns(7)
quick_action = None
labels = ["＋ Test", "＋ Measurement", "＋ DTC", "＋ Hypothesis",
          "＋ Event", "＋ Repair", "＋ Attachment"]
for col, lab in zip(qa, labels):
    if col.button(lab, use_container_width=True, key=f"qa_{lab}"):
        quick_action = lab

# ------------------------------------------------------------------ modal dialogs for quick actions
@st.dialog("Add diagnostic test")
def dlg_test():
    with st.form("qa_test"):
        c1, c2 = st.columns(2)
        system = c1.selectbox("System", [""] + VEHICLE_SYSTEMS)
        component = c2.text_input("Component / circuit")
        procedure = st.text_area("Test performed *", height=70)
        c3, c4 = st.columns(2)
        tool = c3.text_input("Tool used")
        result = c4.selectbox("Result", TEST_RESULTS, index=2)
        c5, c6 = st.columns(2)
        expected = c5.text_input("Expected / spec")
        actual = c6.text_input("Actual")
        conditions = st.text_input("Test conditions")
        interp = st.text_area("Interpretation", height=60)
        proves = st.text_input("What it proves")
        rules_out = st.text_input("What it rules out")
        nxt = st.text_input("Next step")
        if st.form_submit_button("Save test", type="primary") and procedure.strip():
            create_test(case.id, {
                "system": system or None, "component": component or None,
                "procedure": procedure, "tool": tool or None,
                "result": result, "expected": expected or None,
                "actual": actual or None, "conditions": conditions or None,
                "interpretation": interp or None, "proves": proves or None,
                "rules_out": rules_out or None, "next_step": nxt or None,
            })
            st.rerun()


@st.dialog("Add measurement")
def dlg_measurement():
    with st.form("qa_meas"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name *")
        system = c2.selectbox("System", [""] + VEHICLE_SYSTEMS)
        component = st.text_input("Component")
        vt = st.selectbox("Value type", ["numeric", "text", "boolean", "choice"])
        c3, c4, c5 = st.columns(3)
        vnum = c3.number_input("Value (numeric)", value=0.0, step=0.01)
        vtext = c4.text_input("Value (text)")
        units = c5.text_input("Units")
        c6, c7 = st.columns(2)
        smin = c6.number_input("Spec min", value=0.0)
        smax = c7.number_input("Spec max", value=0.0)
        stext = st.text_input("Spec (text)")
        source = st.text_input("Spec source")
        conditions = st.text_input("Test conditions")
        if st.form_submit_button("Save measurement", type="primary") and name.strip():
            create_measurement(case.id, {
                "name": name, "system": system or None,
                "component": component or None, "value_type": vt,
                "value_num": vnum if vt == "numeric" else None,
                "value_text": vtext or None, "units": units or None,
                "spec_min": smin if vt == "numeric" else None,
                "spec_max": smax if vt == "numeric" else None,
                "spec_text": stext or None, "spec_source": source or None,
                "conditions": conditions or None,
            })
            st.rerun()


@st.dialog("Add DTC")
def dlg_dtc():
    with st.form("qa_dtc"):
        c1, c2, c3 = st.columns([1, 2, 1])
        code = c1.text_input("Code *", placeholder="P0335")
        module = c2.text_input("Module")
        status = c3.selectbox("Status", DTC_STATUSES)
        desc = st.text_input("Description")
        ff = st.text_area("Freeze-frame", height=60)
        assoc = st.text_area("Associated symptoms", height=60)
        if st.form_submit_button("Save DTC", type="primary") and code.strip():
            create_dtc(case.id, {
                "code": code.strip().upper(), "module": module or None,
                "status": status, "description": desc or None,
                "freeze_frame": ff or None, "associated_symptoms": assoc or None,
            })
            st.rerun()


@st.dialog("Add hypothesis")
def dlg_hypothesis():
    with st.form("qa_hyp"):
        statement = st.text_area("Statement *", height=60)
        c1, c2 = st.columns(2)
        status = c1.selectbox("Status", HYPOTHESIS_STATUSES)
        conf = c2.slider("Confidence", 0, 100, 50, 5)
        supporting = st.text_area("Supporting evidence", height=60)
        contradicting = st.text_area("Contradicting evidence", height=60)
        if st.form_submit_button("Save hypothesis", type="primary") and statement.strip():
            create_hypothesis(case.id, {
                "statement": statement, "status": status, "confidence": conf,
                "supporting": supporting or None, "contradicting": contradicting or None,
            })
            st.rerun()


@st.dialog("Add timeline event")
def dlg_event():
    with st.form("qa_event"):
        desc = st.text_area("Event *", height=60)
        decision = st.text_input("Decision")
        nxt = st.text_input("Next action")
        when = st.text_input("Time (YYYY-MM-DD HH:MM, blank = now)")
        if st.form_submit_button("Save event", type="primary") and desc.strip():
            ts = None
            if when.strip():
                try:
                    ts = datetime.strptime(when.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                except ValueError:
                    ts = None
            create_event(case.id, desc.strip(), kind="note",
                         decision=decision or None, next_action=nxt or None,
                         occurred_at=ts)
            st.rerun()


@st.dialog("Add repair")
def dlg_repair():
    with st.form("qa_repair"):
        desc = st.text_area("Description *", height=70)
        c1, c2 = st.columns(2)
        parts = c1.text_area("Parts replaced", height=60)
        pnums = c2.text_area("Part numbers", height=60)
        c3, c4 = st.columns(2)
        fluids = c3.text_input("Fluids / materials")
        cal = c4.text_input("Calibration / programming")
        c5, c6 = st.columns(2)
        labor = c5.number_input("Labor (hrs)", value=0.0, step=0.25)
        cost = c6.number_input("Cost", value=0.0, step=1.0)
        why = st.text_area("Why this repair was performed *", height=60)
        if st.form_submit_button("Save repair", type="primary") and desc.strip() and why.strip():
            create_repair(case.id, {
                "description": desc, "parts": parts or None,
                "part_numbers": pnums or None, "fluids": fluids or None,
                "calibration": cal or None, "labor_time": labor or None,
                "cost": cost or None, "why": why,
            })
            st.rerun()


@st.dialog("Add attachment")
def dlg_attachment():
    with st.form("qa_att", clear_on_submit=True):
        up = st.file_uploader("Choose file",
                              type=["jpg", "jpeg", "png", "webp", "gif",
                                    "pdf", "txt", "csv", "json", "md"])
        kind = st.selectbox("Kind", ["photo", "diagram", "screenshot",
                                     "document", "receipt", "other"])
        category = st.selectbox("Category", ["", "complaint", "initial", "test",
                                              "component", "repair", "verification",
                                              "maintenance"])
        caption = st.text_input("Caption")
        notes = st.text_area("Notes", height=60)
        if st.form_submit_button("Upload", type="primary") and up is not None:
            try:
                stored, original, size, mime = save_upload(case.case_number, up)
                create_attachment(case.id, {
                    "kind": kind, "category": category or None,
                    "filename": original, "stored_name": stored,
                    "mime": mime, "size": size,
                    "caption": caption or None, "notes": notes or None,
                })
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")


if quick_action == "＋ Test":
    dlg_test()
elif quick_action == "＋ Measurement":
    dlg_measurement()
elif quick_action == "＋ DTC":
    dlg_dtc()
elif quick_action == "＋ Hypothesis":
    dlg_hypothesis()
elif quick_action == "＋ Event":
    dlg_event()
elif quick_action == "＋ Repair":
    dlg_repair()
elif quick_action == "＋ Attachment":
    dlg_attachment()

st.divider()

# ------------------------------------------------------------------ tabs
tabs = st.tabs([
    "Overview", "Complaint", "Initial", "Scan", "Symptoms", "Plan",
    "Hypotheses", "Tests", "Measurements", "DTCs", "Wiring",
    "Repairs", "Verification", "Remaining", "Safety", "Additional",
    "Timeline", "Attachments", "Reflection", "Costs", "Final", "Report",
])

# Overview tab
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tests", len(case.tests))
    c2.metric("DTCs", len(case.dtcs))
    c3.metric("Measurements", len(case.measurements))
    c4.metric("Repairs", len(case.repairs))
    st.write("")
    new_status = st.selectbox("Case status", ["open", "monitoring", "closed", "archived"],
                              index=["open", "monitoring", "closed", "archived"].index(case.status)
                              if case.status in ["open", "monitoring", "closed", "archived"] else 0)
    if new_status != case.status:
        update_case_meta(case.id, status=new_status,
                         closed_at=datetime.now(timezone.utc) if new_status == "closed" else None)
        st.rerun()
    st.divider()
    st.markdown("##### Recent timeline")
    for e in list_events(case.id)[-8:]:
        st.markdown(f"`{e.occurred_at:%H:%M}` — {e.description}")

# Narrative form tabs
FORM_ORDER = [
    ("Complaint", "complaint"),
    ("Initial", "initial_condition"),
    ("Scan", "scan_data"),
    ("Symptoms", "symptoms"),
    ("Plan", "plan"),
    ("Wiring", "wiring"),
]
for tab, (_, sid) in zip(tabs[1:7], FORM_ORDER):
    with tab:
        section = next((s for s in NARRATIVE_SECTIONS if s["id"] == sid), None)
        if section:
            values = render_section_form(section, getattr(case, SECTION_TO_ATTR[sid], None),
                                         case.case_number)
            if values is not None:
                update_case_section(case.id, SECTION_TO_ATTR[sid], values)
                st.success("Saved.")
                st.rerun()

# Hypotheses tab
with tabs[6]:
    hs = list_hypotheses(case.id)
    if not hs:
        st.info("No hypotheses yet. Use **＋ Hypothesis** above.")
    for h in hs:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{h.label}** — {h.statement}")
            c1.caption(f"Status: {h.status} · Confidence: {h.confidence}%")
            if h.supporting:
                c1.markdown(f"*Supports:* {h.supporting}")
            if h.contradicting:
                c1.markdown(f"*Contradicts:* {h.contradicting}")
            if c2.button("Delete", key=f"del_h_{h.id}"):
                delete_hypothesis(h.id)
                st.rerun()

# Tests tab
with tabs[7]:
    ts = list_tests(case.id)
    if not ts:
        st.info("No tests recorded yet.")
    for t in ts:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{t.procedure}**  ·  `{t.result.upper()}`")
            c1.caption(f"{t.system or ''} · {t.component or ''} · {t.tool or ''}")
            if t.expected or t.actual:
                c1.markdown(f"Expected: {t.expected or '—'}  ·  Actual: **{t.actual or '—'}**")
            if t.interpretation:
                c1.markdown(f"*{t.interpretation}*")
            if t.proves:
                c1.markdown(f"Proves: {t.proves}")
            if t.rules_out:
                c1.markdown(f"Rules out: {t.rules_out}")
            if c2.button("Delete", key=f"del_t_{t.id}"):
                delete_test(t.id)
                st.rerun()

# Measurements tab
with tabs[8]:
    ms = list_measurements(case.id)
    if not ms:
        st.info("No measurements yet.")
    for m in ms:
        with st.container(border=True):
            val = f"{m.value_num} {m.units or ''}" if m.value_num is not None else (m.value_text or "—")
            spec = (f"{m.spec_min} – {m.spec_max} {m.units or ''}"
                    if m.spec_min is not None or m.spec_max is not None
                    else (m.spec_text or "Spec not entered"))
            badge = ""
            if m.in_spec is True:
                badge = '<span class="sg-pill green">IN SPEC</span>'
            elif m.in_spec is False:
                badge = '<span class="sg-pill red">OUT OF SPEC</span>'
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{m.name}** {badge}  —  {val}", unsafe_allow_html=True)
            c1.caption(f"Spec: {spec}  ·  Source: {m.spec_source or '—'}  ·  {m.conditions or ''}")
            if c2.button("Delete", key=f"del_m_{m.id}"):
                delete_measurement(m.id)
                st.rerun()

# DTCs tab
with tabs[9]:
    ds = list_dtcs(case.id)
    if not ds:
        st.info("No DTCs recorded.")
    st.caption("⚠ Code present ≠ root cause confirmed.")
    for d in ds:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f'<span class="sg-pill blue">{d.code}</span> **{d.description or ""}**',
                        unsafe_allow_html=True)
            c1.caption(f"Module: {d.module or '—'} · Status: {d.status}")
            if c2.button("Delete", key=f"del_d_{d.id}"):
                delete_dtc(d.id)
                st.rerun()

# Wiring tab
with tabs[10]:
    st.caption("Wiring fields live on the **Wiring** tab above.")

# Repairs tab
with tabs[11]:
    rs = list_repairs(case.id)
    if not rs:
        st.info("No repairs recorded.")
    for r in rs:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{r.description}**")
            c1.caption(f"{r.performed_at:%Y-%m-%d} · labor {r.labor_time or '—'}h · cost {r.cost or '—'}")
            if r.parts:
                c1.markdown(f"*Parts:* {r.parts}")
            if r.why:
                c1.markdown(f"*Why:* {r.why}")
            if c2.button("Delete", key=f"del_r_{r.id}"):
                delete_repair(r.id)
                st.rerun()

# Verification / Remaining / Safety / Additional / Reflection / Costs / Final
VERIFY_TABS = [
    ("verification", tabs[12]),
    ("remaining", tabs[13]),
    ("safety", tabs[14]),
    ("maintenance_obs", tabs[15]),
    ("reflection", tabs[18]),
    ("costs", tabs[19]),
    ("final_status", tabs[20]),
]
for sid, tab in VERIFY_TABS:
    with tab:
        section = next((s for s in NARRATIVE_SECTIONS if s["id"] == sid), None)
        if section:
            if sid == "reflection":
                st.caption("Private — excluded from customer-facing reports.")
            values = render_section_form(section, getattr(case, SECTION_TO_ATTR[sid], None),
                                         case.case_number)
            if values is not None:
                update_case_section(case.id, SECTION_TO_ATTR[sid], values)
                st.success("Saved.")
                st.rerun()

# Timeline tab
with tabs[16]:
    events = list_events(case.id)
    if not events:
        st.info("No timeline events yet.")
    for e in events:
        tag = "" if not e.auto else ' <span class="sg-pill">auto</span>'
        st.markdown(f"`{e.occurred_at:%Y-%m-%d %H:%M}` — {e.description}{tag}",
                    unsafe_allow_html=True)
        if e.decision:
            st.caption(f"Decision: {e.decision}")
        if e.next_action:
            st.caption(f"Next: {e.next_action}")
    st.divider()
    if st.button("＋ Add timeline event", key="tl_add"):
        dlg_event()

# Attachments tab
with tabs[17]:
    atts = list_attachments(case.id)
    if not atts:
        st.info("No attachments yet. Use **＋ Attachment** above or below.")
    cols = st.columns(3)
    for i, a in enumerate(atts):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{a.caption or a.filename}**")
                st.caption(f"{a.kind} · {a.category or ''} · {a.size or 0:,} B")
                p = attachment_path(case.case_number, a.stored_name)
                if p.exists() and a.mime and a.mime.startswith("image/"):
                    try:
                        st.image(str(p), use_container_width=True)
                    except Exception:
                        st.text("(preview unavailable)")
                if p.exists():
                    with open(p, "rb") as fh:
                        st.download_button("Download", data=fh.read(),
                                           file_name=a.filename,
                                           key=f"dl_{a.id}", use_container_width=True)
                if st.button("Delete", key=f"del_a_{a.id}", use_container_width=True):
                    delete_attachment(a.id)
                    st.rerun()

# Report tab
with tabs[21]:
    st.markdown("#### Report Studio")
    st.caption("Build a professional diagnostic report from this case.")
    if st.button("Open Report Builder for this case", type="primary"):
        st.session_state["nav"] = "Report builder"
        st.rerun()

    st.divider()
    reports = case.reports
    if not reports:
        st.info("No reports generated for this case yet.")
    for r in reports:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{r.name}** · v{r.version}")
            c1.caption(f"{r.report_type} · {r.created_at:%Y-%m-%d %H:%M}")
            if c2.button("Download", key=f"rdl_{r.id}"):
                if r.html:
                    st.download_button("Download HTML", data=r.html,
                                       file_name=f"{case.case_number}_v{r.version}.html",
                                       mime="text/html", key=f"rdlb_{r.id}")
