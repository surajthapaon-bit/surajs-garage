"""Cases list + create."""
from __future__ import annotations

import streamlit as st

from schemas import CASE_CLASSIFICATIONS
from services import create_case, list_cases, list_vehicles

username = st.session_state["username"]
st.markdown("### Diagnostic cases")

open_new = st.session_state.pop("_open_new_case", False)
preset_vid = st.session_state.pop("_new_case_vehicle_id", None)

vehicles = list_vehicles(username)
if not vehicles:
    st.warning("Add a vehicle first (Vehicles page).")
    st.stop()

with st.expander("＋  New case", expanded=open_new):
    with st.form("new_case", clear_on_submit=True):
        opts = {f"{v.nickname} — {v.title}": v.id for v in vehicles}
        labels = list(opts.keys())
        default_idx = 0
        if preset_vid:
            for i, v in enumerate(vehicles):
                if v.id == preset_vid:
                    default_idx = i
                    break
        picked = st.selectbox("Vehicle *", labels, index=default_idx)
        title = st.text_input("Title *", placeholder="Crank / no start")
        classification = st.selectbox("Classification", [""] + CASE_CLASSIFICATIONS)
        if st.form_submit_button("Create case", type="primary") and title.strip():
            cid = create_case(username, opts[picked], title.strip(),
                              classification or None)
            st.session_state["current_case_id"] = cid
            st.session_state["nav"] = "Case workspace"
            st.rerun()

st.divider()
status_filter = st.selectbox("Filter by status", ["all", "open", "monitoring", "closed", "archived"])
cases = list_cases(username, status=None if status_filter == "all" else status_filter)

if not cases:
    st.info("No cases yet.")
for c in cases:
    with st.container(border=True):
        a, b = st.columns([5, 1])
        a.markdown(f"**{c.title}**  ·  {c.vehicle.nickname}")
        a.caption(f"{c.case_number} · {c.status} · {c.opened_at:%Y-%m-%d}")
        if b.button("Open", key=f"c_open_{c.id}", use_container_width=True):
            st.session_state["current_case_id"] = c.id
            st.session_state["nav"] = "Case workspace"
            st.rerun()
