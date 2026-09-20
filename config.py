"""Suraj's Garage — global identity, paths, theme, and helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
ATTACHMENTS_DIR = DATA_DIR / "attachments"
REPORTS_DIR = DATA_DIR / "reports"
BACKUPS_DIR = DATA_DIR / "backups"
DB_PATH = DATA_DIR / "surajs_garage.db"

for _d in (DATA_DIR, ATTACHMENTS_DIR, REPORTS_DIR, BACKUPS_DIR):
    _d.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class GarageConfig:
    name: str = "SURAJ'S GARAGE"
    subtitle: str = "Automotive Diagnostic & Service Journal"
    technician: str = "Suraj Thapa"
    report_title: str = "AUTOMOTIVE DIAGNOSTIC & REPAIR REPORT"
    footer: str = "SURAJ'S GARAGE · Automotive Diagnostic & Service Journal"
    case_prefix: str = "SG"
    mileage_unit: str = "km"
    temperature_unit: str = "°C"
    currency: str = "$"
    doc_version: str = "2.1"
    max_upload_mb: int = 50
    case_url_base: str = os.environ.get("CASE_URL_BASE", "http://localhost:8501")


CONFIG = GarageConfig()


THEME_CSS = """
<style>
/* ── Base ─────────────────────────────────────────────── */
.stApp { background: #0a0a0a; }
section[data-testid="stSidebar"] {
    background: #101010;
    border-right: 1px solid #1e1e1e;
}
header[data-testid="stHeader"] { background: transparent; }

/* ── Brand ────────────────────────────────────────────── */
.sg-brand {
    font-size: 1.18rem; font-weight: 800; letter-spacing: 0.03em;
    color: #f5f5f5; text-transform: uppercase; margin: 0;
}
.sg-sub {
    color: #8a8a8a; font-size: 0.70rem; margin-top: -4px;
    letter-spacing: 0.08em; text-transform: uppercase;
}

/* ── Cards & Metrics ──────────────────────────────────── */
.sg-card {
    background: #131313; border: 1px solid #202020; border-radius: 12px;
    padding: 16px 18px; margin-bottom: 12px;
}
.sg-card h4 { margin: 0 0 4px 0; font-size: 0.95rem; color: #f5f5f5; }
.sg-card p  { margin: 0; color: #a0a0a0; font-size: 0.85rem; }
.sg-metric  { font-size: 1.9rem; font-weight: 700; color: #f5f5f5; line-height: 1.1; }
.sg-label   {
    font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: #7a7a7a;
}

/* ── Pills ────────────────────────────────────────────── */
.sg-pill {
    display: inline-block; padding: 2px 9px; border-radius: 999px;
    font-size: 0.68rem; background: #1e1e1e; color: #c9c9c9;
    margin-right: 6px; letter-spacing: 0.03em;
}
.sg-pill.red   { background: #2a1414; color: #ff9d9d; }
.sg-pill.green { background: #142a18; color: #9dffb3; }
.sg-pill.amber { background: #2a2214; color: #ffd79d; }
.sg-pill.blue  { background: #141f2a; color: #9dc4ff; }

/* ── Buttons & Inputs ─────────────────────────────────── */
div.stButton > button { border-radius: 8px; font-weight: 500; }
div.stButton > button[kind="primary"] { background: #e8e8e8; color: #0a0a0a; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { padding: 6px 14px; font-size: 0.85rem; }
.stTextInput input, .stTextArea textarea, .stNumberInput input { font-size: 0.9rem; }

/* ── Typography ───────────────────────────────────────── */
h1, h2, h3 { letter-spacing: -0.01em; }
</style>
"""


def inject_theme() -> None:
    import streamlit as st
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def metric_card(label: str, value) -> str:
    return (
        f'<div class="sg-card">'
        f'<div class="sg-label">{label}</div>'
        f'<div class="sg-metric">{value}</div></div>'
    )


def pill(text: str, tone: str = "") -> str:
    return f'<span class="sg-pill {tone}">{text}</span>'
