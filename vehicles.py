"""Vehicles list + create. Opens detail via route, not inline render."""
from __future__ import annotations

import streamlit as st

from services import create_vehicle, list_vehicles

username = st.session_state["username"]
st.markdown("### Vehicles")

with st.expander("＋  Add a vehicle", expanded=not list_vehicles(username)):
    with st.form("add_vehicle", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nickname = c1.text_input("Nickname *", placeholder="Daily driver")
        year = c2.number_input("Year", min_value=1900, max_value=2100, value=2017, step=1)
        make = c3.text_input("Make", placeholder="Chevrolet")

        c4, c5, c6 = st.columns(3)
        model = c4.text_input("Model", placeholder="Cruze")
        trim = c5.text_input("Trim")
        vin = c6.text_input("VIN")

        c7, c8, c9 = st.columns(3)
        engine = c7.text_input("Engine")
        engine_code = c8.text_input("Engine code")
        transmission = c9.text_input("Transmission")

        c10, c11, c12 = st.columns(3)
        drivetrain = c10.selectbox("Drivetrain", ["", "FWD", "RWD", "AWD", "4WD"])
        plate = c11.text_input("Plate")
        mileage = c12.number_input("Mileage", min_value=0, value=0, step=100)

        owner_name = st.text_input("Owner / customer name")
        notes = st.text_area("Notes", height=80)

        submitted = st.form_submit_button("Save vehicle", type="primary")
        if submitted and nickname.strip():
            try:
                vid = create_vehicle(username, {
                    "nickname": nickname.strip(),
                    "year": int(year), "make": make or None, "model": model or None,
                    "trim": trim or None, "vin": vin or None,
                    "engine": engine or None, "engine_code": engine_code or None,
                    "transmission": transmission or None,
                    "drivetrain": drivetrain or None,
                    "plate": plate or None, "mileage": int(mileage) or None,
                    "owner_name": owner_name or None,
                    "notes": notes or None, "mods": [],
                })
                st.success(f"Vehicle added (id {vid}).")
                st.rerun()
            except Exception as e:
                st.error(f"Could not save: {e}")

st.divider()
vehicles = list_vehicles(username)
if not vehicles:
    st.info("No vehicles yet.")
else:
    for v in vehicles:
        with st.container(border=True):
            left, right = st.columns([5, 1])
            left.markdown(f"**{v.nickname}** — {v.title}")
            left.caption(f"VIN {v.vin or '—'} · {v.mileage or 0:,} km · {len(v.cases)} case(s)")
            if right.button("Open", key=f"v_open_{v.id}", use_container_width=True):
                st.session_state["current_vehicle_id"] = v.id
                st.session_state["_view_vehicle"] = v.id
                st.session_state["nav"] = "Vehicle detail"
                st.rerun()
