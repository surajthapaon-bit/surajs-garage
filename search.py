"""Global search across the whole record."""
from __future__ import annotations

import streamlit as st

from services import global_search

username = st.session_state["username"]
st.markdown("### Search")

q = st.text_input("Search across vehicles, cases, DTCs, tests, measurements, repairs, events",
                  placeholder='e.g. "P0335" or "fuel pump"')

if not q.strip():
    st.info("Type to search.")
    st.stop()

r = global_search(username, q)

if r["vehicles"]:
    st.markdown("#### Vehicles")
    for v in r["vehicles"]:
        with st.container(border=True):
            st.markdown(f"**{v.nickname}** — {v.title}")
            st.caption(f"VIN {v.vin or '—'}")

for name, key in (("Cases", "cases"), ("DTCs", "dtcs"), ("Tests", "tests"),
                  ("Measurements", "measurements"), ("Repairs", "repairs"),
                  ("Events", "events")):
    rows = r[key]
    if not rows:
        continue
    st.markdown(f"#### {name}")
    for row in rows:
        with st.container(border=True):
            if key == "cases":
                st.markdown(f"**{row.case_number}** — {row.title}")
            elif key == "dtcs":
                st.markdown(f'<span class="sg-pill blue">{row.code}</span> {row.description or ""}',
                            unsafe_allow_html=True)
            elif key == "tests":
                st.markdown(f"**{row.procedure}** — `{row.result}`")
                st.caption(f"{row.component or ''} · {row.system or ''}")
            elif key == "measurements":
                val = f"{row.value_num} {row.units or ''}" if row.value_num is not None else row.value_text
                st.markdown(f"**{row.name}** — {val}")
            elif key == "repairs":
                st.markdown(f"**{row.description}**")
            elif key == "events":
                st.markdown(f"`{row.occurred_at:%Y-%m-%d %H:%M}` — {row.description}")

            if hasattr(row, "case_id"):
                if st.button("Open case", key=f"search_{key}_{row.id}"):
                    st.session_state["current_case_id"] = row.case_id
                    st.session_state["nav"] = "Case workspace"
                    st.rerun()
