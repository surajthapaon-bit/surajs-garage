"""Case library — tags, filters, saved knowledge."""
from __future__ import annotations

import streamlit as st

from schemas import CASE_CLASSIFICATIONS, CASE_TAGS
from services import list_cases, update_case_meta

username = st.session_state["username"]
st.markdown("### Case library")
st.caption("Your personal searchable diagnostic knowledge base.")

cases = list_cases(username)

c1, c2, c3 = st.columns(3)
with c1:
    filt_class = st.selectbox("Classification", ["all"] + CASE_CLASSIFICATIONS)
with c2:
    filt_tag = st.selectbox("Tag", ["all"] + CASE_TAGS)
with c3:
    q = st.text_input("Search title / case #")

def match(c):
    if filt_class != "all" and c.classification != filt_class:
        return False
    if filt_tag != "all" and (not c.tags or filt_tag not in c.tags):
        return False
    if q and q.lower() not in (c.title + " " + c.case_number).lower():
        return False
    return True

filtered = [c for c in cases if match(c)]
st.caption(f"{len(filtered)} case(s)")

for c in filtered:
    with st.container(border=True):
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"**{c.title}**  ·  {c.case_number}")
        c1.caption(f"{c.vehicle.title} · {c.classification or '—'} · "
                   f"tags: {', '.join(c.tags or []) or '—'}")
        if c2.button("Open", key=f"lib_{c.id}", use_container_width=True):
            st.session_state["current_case_id"] = c.id
            st.session_state["nav"] = "Case workspace"
            st.rerun()

        new_tags = st.multiselect("Tags", CASE_TAGS, default=c.tags or [],
                                   key=f"tags_{c.id}")
        if new_tags != (c.tags or []):
            update_case_meta(c.id, tags=new_tags)
            st.rerun()
