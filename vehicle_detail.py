"""Vehicle profile + complete chronological history."""
from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from services import get_vehicle, list_cases, list_maintenance

vid = st.session_state.get("_view_vehicle") or st.session_state.get("current_vehicle_id")
if not vid:
    st.warning("Open a vehicle from the Vehicles page.")
    st.stop()

v = get_vehicle(vid)
if not v:
    st.error("Vehicle not found.")
    st.stop()

if st.button("← Back to vehicles"):
    st.session_state.pop("_view_vehicle", None)
    st.session_state["nav"] = "Vehicles"
    st.rerun()

st.markdown(f"## {v.nickname}")
st.caption(v.title)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Year", v.year or "—")
c2.metric("Make", v.make or "—")
c3.metric("Model", v.model or "—")
c4.metric("Mileage", f"{v.mileage:,}" if v.mileage else "—")

st.write("")
with st.expander("Vehicle details", expanded=False):
    st.markdown(f"**VIN:** {v.vin or '—'}")
    st.markdown(f"**Trim:** {v.trim or '—'}")
    st.markdown(f"**Engine:** {v.engine or '—'}  ({v.engine_code or '—'})")
    st.markdown(f"**Transmission:** {v.transmission or '—'}")
    st.markdown(f"**Drivetrain:** {v.drivetrain or '—'}")
    st.markdown(f"**Plate:** {v.plate or '—'}")
    st.markdown(f"**Owner:** {v.owner_name or '—'}")
    if v.notes:
        st.markdown(f"**Notes:** {v.notes}")
    if v.mods:
        st.markdown(f"**Modifications:** {', '.join(v.mods)}")

st.divider()
st.markdown("### Complete History")

cases = list_cases(v.owner, vehicle_id=v.id)
maint = list_maintenance(v.id)

feed = []
for c in cases:
    feed.append((c.opened_at, "case", c))
for m in maint:
    feed.append((m.created_at or datetime.now(timezone.utc), "maintenance", m))
feed.sort(key=lambda x: x[0] or datetime.now(timezone.utc), reverse=True)

if not feed:
    st.info("No history yet — open a case for this vehicle.")
else:
    for ts, kind, obj in feed:
        if kind == "case":
            with st.container(border=True):
                a, b = st.columns([5, 1])
                a.markdown(f"**{obj.title}**  ·  {obj.case_number}")
                a.caption(f"{obj.opened_at:%Y-%m-%d} · status: {obj.status} · "
                          f"{len(obj.tests)} tests, {len(obj.dtcs)} DTCs, {len(obj.repairs)} repairs")
                if b.button("Open case", key=f"vh_{obj.id}", use_container_width=True):
                    st.session_state["current_case_id"] = obj.id
                    st.session_state["nav"] = "Case workspace"
                    st.rerun()
        else:
            st.markdown(f"**{obj.kind}** — {obj.notes or ''}  ·  *{ts:%Y-%m-%d}*")

st.divider()
if st.button("＋  New diagnostic case for this vehicle", type="primary"):
    st.session_state["_new_case_vehicle_id"] = v.id
    st.session_state["nav"] = "Cases"
    st.session_state["_open_new_case"] = True
    st.rerun()
