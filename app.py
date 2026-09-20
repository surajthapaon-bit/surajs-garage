"""Suraj's Garage — application entry point."""
from __future__ import annotations

import runpy

import streamlit as st

from auth import require_login
from config import CONFIG, inject_theme
from db import init_db

st.set_page_config(
    page_title=f"{CONFIG.name} — {CONFIG.subtitle}",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_theme()

name, username, auth = require_login()
st.session_state["username"] = username
st.session_state["display_name"] = name

# --- deep link ?case=SG-YYYYMMDD-### (one-shot) ---
try:
    qp = st.query_params
    deep_case = qp.get("case") if hasattr(qp, "get") else None
except Exception:
    deep_case = None

if deep_case:
    from db import session_scope, DiagnosticCase
    from sqlalchemy import select
    matched = False
    try:
        with session_scope() as s:
            c = s.scalar(select(DiagnosticCase).where(
                DiagnosticCase.case_number == deep_case))
            if c and c.vehicle.owner == username:
                st.session_state["current_case_id"] = c.id
                st.session_state["nav"] = "Case workspace"
                matched = True
    except Exception:
        matched = False
    # Always clear the param so navigation is not hijacked on every rerun.
    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(f'<div class="sg-brand">{CONFIG.name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sg-sub">{CONFIG.subtitle}</div>', unsafe_allow_html=True)
    st.write("")

    if st.button("＋  New diagnostic case", use_container_width=True, type="primary"):
        st.session_state["nav"] = "Cases"
        st.session_state["_open_new_case"] = True
        st.rerun()

    st.write("")
    nav_options = [
        "Dashboard", "Vehicles", "Vehicle detail", "Cases",
        "Case workspace", "Case library", "Report builder", "Search", "Settings",
    ]
    current_nav = st.session_state.get("nav", "Dashboard")
    if current_nav not in nav_options:
        current_nav = "Dashboard"
    nav = st.radio(
        "Navigate", nav_options,
        index=nav_options.index(current_nav),
        label_visibility="collapsed", key="nav_radio",
    )
    st.session_state["nav"] = nav

    st.write("")
    st.divider()
    st.caption(f"Signed in as **{name}**")
    auth.logout(location="sidebar", button_name="Sign out", key="logout_widget")

# ---------------------------------------------------------------- routing
ROUTES = {
    "Dashboard":       "views/dashboard.py",
    "Vehicles":        "views/vehicles.py",
    "Vehicle detail":  "views/vehicle_detail.py",
    "Cases":           "views/cases.py",
    "Case workspace":  "views/case_workspace.py",
    "Case library":    "views/case_library.py",
    "Report builder":  "views/report_builder.py",
    "Search":          "views/search.py",
    "Settings":        "views/settings.py",
}

runpy.run_path(ROUTES.get(nav, "views/dashboard.py"), run_name="__page__")
