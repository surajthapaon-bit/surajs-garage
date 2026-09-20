"""Report Builder / Print Studio."""
from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from config import CONFIG, REPORTS_DIR
from reports import (
    BUILTIN_TEMPLATES, SECTION_REGISTRY, blocks_to_html, generate_pdf,
)
from services import get_case, list_cases, save_report, create_template

username = st.session_state["username"]
st.markdown("### Report builder")
st.caption("Case data → select content → arrange → preview → generate → print / PDF.")

cases = list_cases(username)
if not cases:
    st.warning("No cases yet.")
    st.stop()

# ---------------------------------------------------------------- case pick
current_id = st.session_state.get("current_case_id")
idx = 0
if current_id:
    for i, c in enumerate(cases):
        if c.id == current_id:
            idx = i
            break
labels = [f"{c.case_number} — {c.title}" for c in cases]
picked = st.selectbox("Case", labels, index=idx)
case = get_case(cases[labels.index(picked)].id)
st.session_state["current_case_id"] = case.id

st.divider()

# ---------------------------------------------------------------- template pick
c1, c2 = st.columns([2, 1])
with c1:
    template_name = st.selectbox(
        "Template", ["Custom"] + list(BUILTIN_TEMPLATES.keys()),
        help="Choose a template to pre-select sections, or Custom to pick manually.",
    )
with c2:
    audience = st.selectbox("Audience", ["internal", "customer", "inspection", "repair"])

# default sections
if template_name == "Custom":
    default_sections = ["vehicle", "complaint", "dtcs", "root_cause", "repairs",
                        "verification", "summary", "signature"]
else:
    default_sections = list(BUILTIN_TEMPLATES[template_name]["sections"])

all_keys = list(SECTION_REGISTRY.keys())
labels_map = {k: SECTION_REGISTRY[k][0] for k in all_keys}

selected = st.multiselect(
    "Sections to include (in order)",
    options=all_keys,
    default=default_sections,
    format_func=lambda k: labels_map[k],
)

# Title override
title = st.text_input("Report title", value=CONFIG.report_title)

# private options
if any(s == "reflection" for s in selected):
    include_private = st.checkbox("Include private technician reflection",
                                  value=(audience == "internal"))
else:
    include_private = False

st.caption("🔒 Private technician notes are excluded from customer-facing reports by default."
           if audience != "internal" else "ℹ️ This report includes internal-only content.")

# Save as template
with st.expander("Save current selection as template"):
    tmpl_name = st.text_input("Template name")
    if st.button("Save template") and tmpl_name.strip():
        create_template(username, tmpl_name.strip(), audience, selected)
        st.success(f"Template '{tmpl_name}' saved.")

st.divider()

# ---------------------------------------------------------------- preview
if st.button("Preview report", type="primary"):
    html = blocks_to_html(case, selected, {"include_private": include_private,
                                            "title": title})
    st.session_state["_report_preview_html"] = html
    st.session_state["_report_preview_title"] = title

html = st.session_state.get("_report_preview_html")
if html:
    st.markdown("#### Preview")
    components.html(html, height=700, scrolling=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇  Download HTML", data=html,
                           file_name=f"{case.case_number}_report.html",
                           mime="text/html", use_container_width=True)
    with c2:
        if st.button("Generate PDF", use_container_width=True):
            out = REPORTS_DIR / case.case_number / \
                  f"{case.case_number}_v{len(case.reports) + 1}.pdf"
            try:
                generate_pdf(case, selected, out,
                             {"include_private": include_private, "title": title})
                st.success(f"PDF generated: {out.name}")
                with open(out, "rb") as fh:
                    st.download_button("⬇  Download PDF", data=fh.read(),
                                       file_name=out.name, mime="application/pdf",
                                       key="pdf_dl", use_container_width=True)
            except Exception as e:
                st.error(f"PDF failed: {e}")
    with c3:
        if st.button("Save to case history", use_container_width=True):
            try:
                out = REPORTS_DIR / case.case_number / \
                      f"{case.case_number}_v{len(case.reports) + 1}.pdf"
                generate_pdf(case, selected, out,
                             {"include_private": include_private, "title": title})
                save_report(case.id, title, audience,
                            template_name if template_name != "Custom" else None,
                            selected, html, str(out),
                            {"title": title, "include_private": include_private})
                st.success("Report saved to case history.")
            except Exception as e:
                st.error(f"Save failed: {e}")
