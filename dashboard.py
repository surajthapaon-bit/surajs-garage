"""Dashboard — active cases, quick actions, recent activity."""
from __future__ import annotations

import streamlit as st
from sqlalchemy import select, func

from config import metric_card, CONFIG
from db import DiagnosticCase, DTC, Vehicle, session_scope
from services import list_cases, list_vehicles

username = st.session_state["username"]
st.markdown("### Overview")
st.caption("Document facts. Record tests. Separate suspicion from confirmation.")
st.write("")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("＋  New case", use_container_width=True, type="primary"):
        st.session_state["nav"] = "Cases"
        st.session_state["_open_new_case"] = True
        st.rerun()
with c2:
    if st.button("Vehicles", use_container_width=True):
        st.session_state["nav"] = "Vehicles"
        st.rerun()
with c3:
    if st.button("Case library", use_container_width=True):
        st.session_state["nav"] = "Case library"
        st.rerun()
with c4:
    if st.button("Report builder", use_container_width=True):
        st.session_state["nav"] = "Report builder"
        st.rerun()

st.write("")

with session_scope() as s:
    veh_ids = [v.id for v in s.scalars(select(Vehicle).where(Vehicle.owner == username))]

    active = 0
    awaiting = 0
    total_cases = 0
    recent_dtcs = []
    if veh_ids:
        active = s.scalar(select(func.count()).select_from(DiagnosticCase)
                          .where(DiagnosticCase.vehicle_id.in_(veh_ids),
                                 DiagnosticCase.status == "open")) or 0
        awaiting = s.scalar(select(func.count()).select_from(DiagnosticCase)
                            .where(DiagnosticCase.vehicle_id.in_(veh_ids),
                                   DiagnosticCase.status == "monitoring")) or 0
        total_cases = s.scalar(select(func.count()).select_from(DiagnosticCase)
                               .where(DiagnosticCase.vehicle_id.in_(veh_ids))) or 0
        recent_dtcs = list(s.scalars(
            select(DTC).join(DiagnosticCase)
            .where(DiagnosticCase.vehicle_id.in_(veh_ids))
            .order_by(DTC.created_at.desc()).limit(6)
        ))

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(metric_card("Vehicles", len(list_vehicles(username))), unsafe_allow_html=True)
with m2:
    st.markdown(metric_card("Active cases", active), unsafe_allow_html=True)
with m3:
    st.markdown(metric_card("Awaiting verification", awaiting), unsafe_allow_html=True)
with m4:
    st.markdown(metric_card("Total cases", total_cases), unsafe_allow_html=True)

st.write("")
st.markdown("#### Recent cases")
cases = list_cases(username)[:6]
if not cases:
    st.info("No diagnostic cases yet. Use **＋ New case** above.")
else:
    for c in cases:
        with st.container(border=True):
            a, b = st.columns([5, 1])
            a.markdown(f"**{c.title}**  ·  {c.vehicle.nickname}")
            a.caption(f"{c.case_number} · {c.status} · opened {c.opened_at:%Y-%m-%d}")
            if b.button("Open", key=f"dash_open_{c.id}", use_container_width=True):
                st.session_state["current_case_id"] = c.id
                st.session_state["nav"] = "Case workspace"
                st.rerun()

if recent_dtcs:
    st.write("")
    st.markdown("#### Recent DTCs")
    for d in recent_dtcs:
        st.markdown(
            f'<span class="sg-pill blue">{d.code}</span>'
            f' <span style="color:#9a9a9a;">{d.description or ""}</span>',
            unsafe_allow_html=True,
        )
