"""Render a schema section into Streamlit widgets. Returns collected values."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from schemas import REQ_LABEL


def _label(field: dict) -> str:
    return f"{field['label']}  ·  [{REQ_LABEL[field['req']]}]"


def _render_field(section_id: str, field: dict, current):
    key = f"f__{section_id}__{field['key']}"
    t = field["type"]
    label = _label(field)

    if t == "text":
        return st.text_input(label, value=current or "", key=key)
    if t == "number":
        try:
            v = float(current) if current not in (None, "") else 0.0
        except (TypeError, ValueError):
            v = 0.0
        return st.number_input(label, value=v, key=key)
    if t == "date":
        return st.text_input(label, value=current or "", key=key)
    if t == "text_area":
        return st.text_area(label, value=current or "", height=90, key=key)
    if t == "select":
        opts = field.get("options") or [""]
        if not opts or opts[0] != "":
            opts = [""] + list(opts)
        idx = opts.index(current) if current in opts else 0
        return st.selectbox(label, opts, index=idx, key=key)
    if t == "multi":
        opts = field.get("options") or []
        preset = [v for v in (current or []) if v in opts]
        return st.multiselect(label, opts, default=preset, key=key)
    if t == "check":
        return st.checkbox(label, value=bool(current), key=key)
    if t == "table":
        import math
        cols = field.get("columns") or []
        rows = current if isinstance(current, list) and current else [{} for _ in range(2)]
        df = pd.DataFrame(rows, columns=cols)
        edited = st.data_editor(
            df, num_rows="dynamic", use_container_width=True,
            key=f"t__{section_id}__{field['key']}",
        )
        records = edited.to_dict("records")
        cleaned = []
        for r in records:
            if all(
                v is None or v == "" or (isinstance(v, float) and math.isnan(v))
                for v in r.values()
            ):
                continue
            cleaned.append({
                k: (None if isinstance(v, float) and math.isnan(v) else v)
                for k, v in r.items()
            })
        return cleaned

    return None


def render_section_form(section: dict, existing: dict | None, case_number: str):
    """Render one section as a form. Returns submitted values or None."""
    existing = existing or {}
    with st.form(f"form__{case_number}__{section['id']}", clear_on_submit=False):
        if section.get("subtitle"):
            st.caption(section["subtitle"])
        values: dict = {}
        for field in section["fields"]:
            values[field["key"]] = _render_field(section["id"], field, existing.get(field["key"]))
        submitted = st.form_submit_button("💾  Save section", type="primary", use_container_width=True)
    return values if submitted else None


def render_section_readonly(section: dict, existing: dict | None) -> None:
    """Read-only render (used in print preview only — actual UI uses forms)."""
    existing = existing or {}
    st.markdown(f"**{section['title']}**")
    if section.get("subtitle"):
        st.caption(section["subtitle"])
    for field in section["fields"]:
        v = existing.get(field["key"])
        if v in (None, "", [], {}):
            continue
        if isinstance(v, list) and v and isinstance(v[0], dict):
            st.markdown(f"*{field['label']}*")
            st.dataframe(pd.DataFrame(v), use_container_width=True)
        else:
            st.markdown(f"**{field['label']}:** {v}")
