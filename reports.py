"""Suraj's Garage — Report Builder & Print Studio.

Block-based report system. Case data → section renderers → blocks →
HTML preview / PDF. Templates save section selections and options.

The report is a PRESENTATION of the case record — never a duplicate.
"""
from __future__ import annotations

import html as html_lib
from datetime import datetime, timezone
from pathlib import Path

from config import CONFIG, REPORTS_DIR
from db import DiagnosticCase


def _has(v) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return True


def _kv_block(title: str, pairs: list[tuple[str, object]]) -> dict:
    return {"type": "kv", "title": title,
            "rows": [(k, str(v)) for k, v in pairs if _has(v)]}


def _table_block(title: str, columns: list[str], rows: list[dict]) -> dict:
    if not rows:
        return {"type": "table", "title": title, "columns": columns, "rows": []}
    return {"type": "table", "title": title, "columns": columns, "rows": rows}


# ---------------------------------------------------------------- section renderers
def sec_vehicle(case: DiagnosticCase) -> list[dict]:
    v = case.vehicle
    pairs = [
        ("Case number", case.case_number),
        ("Date opened", case.opened_at.strftime("%Y-%m-%d %H:%M") if case.opened_at else ""),
        ("Nickname", v.nickname),
        ("Year", v.year), ("Make", v.make), ("Model", v.model), ("Trim", v.trim),
        ("VIN", v.vin), ("Engine", v.engine), ("Engine code", v.engine_code),
        ("Transmission", v.transmission), ("Drivetrain", v.drivetrain),
        ("Mileage", f"{v.mileage:,} {CONFIG.mileage_unit}" if v.mileage else ""),
        ("Plate", v.plate), ("Owner", v.owner_name),
    ]
    return [{"type": "heading", "text": "Vehicle Identification"},
            _kv_block("Vehicle", pairs)]


def sec_complaint(case: DiagnosticCase) -> list[dict]:
    d = case.complaint or {}
    if not d:
        return []
    pairs = [
        ("Customer statement", d.get("statement")),
        ("Problem started", d.get("started")),
        ("Conditions", d.get("conditions")),
        ("Frequency", d.get("frequency")),
        ("Recent repairs", d.get("recent_repairs")),
        ("Recent parts", d.get("recent_parts")),
        ("Weather / temperature", d.get("weather")),
        ("Prior diagnosis", d.get("prior_tech")),
    ]
    return [{"type": "heading", "text": "Customer Complaint"},
            _kv_block("Reported concern", pairs)]


def sec_initial_condition(case: DiagnosticCase) -> list[dict]:
    d = case.initial_condition or {}
    if not d:
        return []
    pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
    return [{"type": "heading", "text": "Initial Vehicle Condition"},
            _kv_block("Condition at arrival", pairs)]


def sec_scan_data(case: DiagnosticCase) -> list[dict]:
    d = case.scan_data or {}
    if not d:
        return []
    pairs = [
        ("Scan tool", d.get("scan_tool")),
        ("Software", d.get("software")),
        ("Communication status", d.get("comm_status")),
        ("Modules scanned", d.get("modules")),
        ("System voltage", d.get("system_voltage")),
        ("Live-data observations", d.get("live_data")),
        ("Readiness monitors", d.get("readiness")),
    ]
    return [{"type": "heading", "text": "Initial Diagnostic Data"},
            _kv_block("Scan tool", pairs)]


def sec_dtcs(case: DiagnosticCase) -> list[dict]:
    if not case.dtcs:
        return []
    rows = [{
        "Code": d.code, "Module": d.module or "", "Status": d.status,
        "Description": d.description or "",
    } for d in case.dtcs]
    return [{"type": "heading", "text": "Diagnostic Trouble Codes"},
            {"type": "warning",
             "text": "Code present ≠ root cause confirmed. Confirmation requires an evidential test."},
            _table_block("DTCs", ["Code", "Module", "Status", "Description"], rows)]


def sec_symptoms(case: DiagnosticCase) -> list[dict]:
    d = case.symptoms or {}
    if not d:
        return []
    pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
    return [{"type": "heading", "text": "Symptom Reproduction"},
            _kv_block("Symptom", pairs)]


def sec_plan(case: DiagnosticCase) -> list[dict]:
    d = case.plan or {}
    if not d:
        return []
    systems = ", ".join(d.get("systems") or [])
    pairs = [
        ("Suspected systems", systems),
        ("Initial hypothesis", d.get("hypothesis")),
        ("Evidence for", d.get("evidence_for")),
        ("Evidence against", d.get("evidence_against")),
        ("Next test", d.get("next_test")),
        ("Expected", d.get("expected")),
        ("Actual", d.get("actual")),
    ]
    return [{"type": "heading", "text": "Diagnostic Plan"},
            _kv_block("Plan", pairs)]


def sec_hypotheses(case: DiagnosticCase) -> list[dict]:
    if not case.hypotheses:
        return []
    rows = [{
        "Label": h.label, "Statement": h.statement, "Status": h.status,
        "Confidence": f"{h.confidence}%",
        "Supporting": h.supporting or "", "Contradicting": h.contradicting or "",
    } for h in case.hypotheses]
    return [{"type": "heading", "text": "Diagnostic Hypotheses"},
            _table_block("Hypotheses",
                         ["Label", "Statement", "Status", "Confidence",
                          "Supporting", "Contradicting"], rows)]


def sec_tests(case: DiagnosticCase) -> list[dict]:
    if not case.tests:
        return []
    rows = [{
        "#": i + 1,
        "System": t.system or "",
        "Component": t.component or "",
        "Test": t.procedure,
        "Expected": t.expected or "",
        "Actual": t.actual or "",
        "Result": t.result.upper(),
        "Proves": t.proves or "",
        "Rules out": t.rules_out or "",
    } for i, t in enumerate(case.tests)]
    return [{"type": "heading", "text": "Diagnostic Test Log"},
            _table_block("Tests",
                         ["#", "System", "Component", "Test", "Expected",
                          "Actual", "Result", "Proves", "Rules out"], rows)]


def sec_measurements(case: DiagnosticCase) -> list[dict]:
    if not case.measurements:
        return []
    rows = []
    for m in case.measurements:
        val = ""
        if m.value_num is not None:
            val = f"{m.value_num} {m.units or ''}".strip()
        elif m.value_text:
            val = m.value_text
        spec = ""
        if m.spec_min is not None or m.spec_max is not None:
            spec = f"{m.spec_min} – {m.spec_max} {m.units or ''}".strip()
        elif m.spec_text:
            spec = m.spec_text
        in_spec = m.in_spec
        status = "" if in_spec is None else ("IN SPEC" if in_spec else "OUT OF SPEC")
        rows.append({
            "Measurement": m.name, "Spec": spec or "Spec not entered",
            "Actual": val, "Conditions": m.conditions or "",
            "Source": m.spec_source or "", "Status": status,
        })
    return [{"type": "heading", "text": "Measurements"},
            _table_block("Measurements",
                         ["Measurement", "Spec", "Actual", "Conditions",
                          "Source", "Status"], rows)]


def sec_wiring(case: DiagnosticCase) -> list[dict]:
    d = case.wiring or {}
    if not d:
        return []
    pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
    return [{"type": "heading", "text": "Wiring / Electrical"},
            _kv_block("Circuit data", pairs)]


def sec_root_cause(case: DiagnosticCase) -> list[dict]:
    d = case.root_cause or {}
    if not d:
        return []
    pairs = [
        ("Symptom", d.get("symptom")),
        ("Failure", d.get("failure")),
        ("Root cause", d.get("root_cause")),
        ("Contributing factors", d.get("contributing")),
        ("Evidence", d.get("evidence")),
        ("Confidence", d.get("confidence")),
    ]
    return [{"type": "heading", "text": "Root-Cause Analysis"},
            _kv_block("Analysis", pairs)]


def sec_repairs(case: DiagnosticCase) -> list[dict]:
    blocks = [{"type": "heading", "text": "Repair Performed"}]
    if case.repairs:
        rows = [{
            "Date": r.performed_at.strftime("%Y-%m-%d") if r.performed_at else "",
            "Description": r.description, "Parts": r.parts or "",
            "Labor (h)": r.labor_time or "", "Cost": r.cost or "",
        } for r in case.repairs]
        blocks.append(_table_block("Repairs", ["Date", "Description", "Parts",
                                                "Labor (h)", "Cost"], rows))
    d = case.repair_notes or {}
    if d:
        pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
        blocks.append(_kv_block("Repair notes", pairs))
    return blocks if len(blocks) > 1 else []


def sec_verification(case: DiagnosticCase) -> list[dict]:
    d = case.verification or {}
    if not d:
        return []
    pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
    return [{"type": "heading", "text": "Post-Repair Verification"},
            _kv_block("Verification", pairs)]


def sec_remaining(case: DiagnosticCase) -> list[dict]:
    d = case.remaining or {}
    issues = d.get("issues") if isinstance(d, dict) else None
    if not issues:
        return []
    return [{"type": "heading", "text": "Remaining Issues"},
            _table_block("Open issues",
                         ["Issue", "Severity", "Safety-relevant?", "Status",
                          "Next step", "Parts needed", "Additional testing", "Priority"],
                         issues)]


def sec_safety(case: DiagnosticCase) -> list[dict]:
    d = case.safety or {}
    items = d.get("safety_items") if isinstance(d, dict) else None
    if not items:
        return []
    return [{"type": "heading", "text": "Safety / Roadworthiness"},
            _table_block("Safety", ["Area", "Finding", "Diagnostic vs Safety-critical"], items)]


def sec_maintenance_obs(case: DiagnosticCase) -> list[dict]:
    d = case.maintenance_obs or {}
    items = d.get("obs") if isinstance(d, dict) else None
    if not items:
        return []
    return [{"type": "heading", "text": "Additional Observations"},
            _table_block("Observations", ["Item", "Observation", "Recommended action"], items)]


def sec_timeline(case: DiagnosticCase) -> list[dict]:
    if not case.events:
        return []
    rows = [{
        "Time": e.occurred_at.strftime("%H:%M") if e.occurred_at else "",
        "Event": e.description, "Decision": e.decision or "",
        "Next": e.next_action or "",
    } for e in case.events]
    return [{"type": "heading", "text": "Diagnostic Timeline"},
            _table_block("Timeline", ["Time", "Event", "Decision", "Next"], rows)]


def sec_photos(case: DiagnosticCase) -> list[dict]:
    photos = [a for a in case.attachments if a.kind == "photo"]
    if not photos:
        return []
    items = [{
        "path": a.stored_name, "caption": a.caption or a.filename,
        "case_number": case.case_number,
    } for a in photos]
    return [{"type": "heading", "text": "Photographic Evidence"},
            {"type": "photo_grid", "items": items}]


def sec_attachments(case: DiagnosticCase) -> list[dict]:
    if not case.attachments:
        return []
    rows = [{
        "#": i + 1, "Filename": a.filename, "Kind": a.kind,
        "Category": a.category or "", "Caption": a.caption or "",
    } for i, a in enumerate(case.attachments)]
    return [{"type": "heading", "text": "Attachment Log"},
            _table_block("Attachments", ["#", "Filename", "Kind", "Category", "Caption"], rows)]


def sec_summary(case: DiagnosticCase) -> list[dict]:
    d = case.summary or {}
    if not d:
        return []
    pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
    return [{"type": "heading", "text": "Final Diagnostic Summary"},
            _kv_block("Summary", pairs)]


def sec_final_status(case: DiagnosticCase) -> list[dict]:
    d = case.final_status or {}
    statuses = d.get("status") if isinstance(d, dict) else None
    if not statuses:
        return []
    return [{"type": "heading", "text": "Final Status"},
            {"type": "paragraph", "text": ", ".join(statuses)}]


def sec_reflection(case: DiagnosticCase) -> list[dict]:
    d = case.reflection or {}
    if not d:
        return []
    pairs = [(k.replace("_", " ").title(), v) for k, v in d.items()]
    return [{"type": "heading", "text": "Technician Reflection (Internal)"},
            {"type": "warning", "text": "Private — excluded from customer reports."},
            _kv_block("Reflection", pairs)]


def sec_signature(case: DiagnosticCase) -> list[dict]:
    return [{"type": "divider"},
            {"type": "signature",
             "left": [("Technician", CONFIG.technician), ("Date", "")],
             "right": [("Reviewed by", ""), ("Date", "")]}]


SECTION_REGISTRY = {
    "vehicle":         ("Vehicle Identification", sec_vehicle),
    "complaint":       ("Customer Complaint", sec_complaint),
    "initial":         ("Initial Condition", sec_initial_condition),
    "scan":            ("Scan Data", sec_scan_data),
    "dtcs":            ("DTCs", sec_dtcs),
    "symptoms":        ("Symptom Reproduction", sec_symptoms),
    "plan":            ("Diagnostic Plan", sec_plan),
    "hypotheses":      ("Hypotheses", sec_hypotheses),
    "tests":           ("Diagnostic Tests", sec_tests),
    "measurements":    ("Measurements", sec_measurements),
    "wiring":          ("Wiring / Electrical", sec_wiring),
    "root_cause":      ("Root Cause", sec_root_cause),
    "repairs":         ("Repair", sec_repairs),
    "verification":    ("Verification", sec_verification),
    "remaining":       ("Remaining Issues", sec_remaining),
    "safety":          ("Safety", sec_safety),
    "maintenance_obs": ("Additional Observations", sec_maintenance_obs),
    "timeline":        ("Timeline", sec_timeline),
    "photos":          ("Photos", sec_photos),
    "attachments":     ("Attachments", sec_attachments),
    "summary":         ("Final Summary", sec_summary),
    "final_status":    ("Final Status", sec_final_status),
    "reflection":      ("Technician Reflection", sec_reflection),
    "signature":       ("Signature Block", sec_signature),
}


# ================================================================== templates
BUILTIN_TEMPLATES = {
    "Full Diagnostic Report": {
        "audience": "internal",
        "sections": ["vehicle", "complaint", "initial", "scan", "dtcs", "symptoms",
                     "plan", "hypotheses", "tests", "measurements", "wiring",
                     "root_cause", "repairs", "verification", "remaining",
                     "safety", "maintenance_obs", "timeline", "photos",
                     "attachments", "summary", "final_status", "reflection",
                     "signature"],
    },
    "Customer Service Report": {
        "audience": "customer",
        "sections": ["vehicle", "complaint", "dtcs", "root_cause", "repairs",
                     "verification", "remaining", "safety", "summary",
                     "final_status", "signature"],
    },
    "Internal Diagnostic Report": {
        "audience": "internal",
        "sections": ["vehicle", "complaint", "initial", "scan", "dtcs", "symptoms",
                     "plan", "hypotheses", "tests", "measurements", "wiring",
                     "root_cause", "reflection", "timeline"],
    },
    "Inspection Report": {
        "audience": "customer",
        "sections": ["vehicle", "initial", "measurements", "safety",
                     "maintenance_obs", "summary", "signature"],
    },
    "Repair Record": {
        "audience": "customer",
        "sections": ["vehicle", "complaint", "root_cause", "repairs",
                     "verification", "final_status", "signature"],
    },
}


# ================================================================== HTML render
def _esc(s) -> str:
    return html_lib.escape(str(s)) if s not in (None, "") else ""


def blocks_to_html(case: DiagnosticCase, section_keys: list[str],
                   options: dict | None = None) -> str:
    options = options or {}
    include_private = options.get("include_private", False)
    title = options.get("title") or CONFIG.report_title
    v = case.vehicle

    parts: list[str] = []
    parts.append(_cover(case, title, v, options))

    for key in section_keys:
        entry = SECTION_REGISTRY.get(key)
        if not entry:
            continue
        if key == "reflection" and not include_private:
            continue
        _, fn = entry
        try:
            blocks = fn(case)
        except Exception as e:
            blocks = [{"type": "warning", "text": f"Section error: {e}"}]
        for block in blocks:
            parts.append(_block_html(block, case))

    parts.append(_footer_html(case))
    return _html_doc(title, "\n".join(parts))


def _cover(case: DiagnosticCase, title: str, v, options: dict) -> str:
    mileage = f"{v.mileage:,} {CONFIG.mileage_unit}" if v.mileage else "—"
    return f"""
    <section class="cover">
      <div class="brand">{_esc(CONFIG.name)}</div>
      <div class="brand-sub">{_esc(CONFIG.subtitle)}</div>
      <hr/>
      <h1>{_esc(title)}</h1>
      <div class="cover-meta">
        <div><strong>Vehicle:</strong> {_esc(v.title)}</div>
        <div><strong>Case:</strong> {_esc(case.case_number)}</div>
        <div><strong>VIN:</strong> {_esc(v.vin or '—')}</div>
        <div><strong>Mileage:</strong> {_esc(mileage)}</div>
        <div><strong>Date:</strong> {datetime.now(timezone.utc).strftime('%B %d, %Y')}</div>
        <div><strong>Technician:</strong> {_esc(CONFIG.technician)}</div>
      </div>
    </section>
    <div class="page-break"></div>
    """


def _block_html(b: dict, case: DiagnosticCase) -> str:
    t = b["type"]
    if t == "heading":
        return f'<h2 class="sec">{_esc(b["text"])}</h2>'
    if t == "paragraph":
        return f'<p>{_esc(b["text"])}</p>'
    if t == "warning":
        return f'<div class="warn">⚠ {_esc(b["text"])}</div>'
    if t == "divider":
        return "<hr/>"
    if t == "kv":
        rows = b.get("rows") or []
        if not rows:
            return ""
        body = "".join(
            f'<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>' for k, v in rows
        )
        title = b.get("title")
        head = f'<h3>{_esc(title)}</h3>' if title else ""
        return f'{head}<table class="kv">{body}</table>'
    if t == "table":
        cols = b.get("columns") or []
        rows = b.get("rows") or []
        if not rows:
            return f'<h3>{_esc(b.get("title") or "")}</h3><p class="empty">No records.</p>'
        head = "".join(f"<th>{_esc(c)}</th>" for c in cols)
        body = ""
        for r in rows:
            cells = "".join(f"<td>{_esc(r.get(c, ''))}</td>" for c in cols)
            body += f"<tr>{cells}</tr>"
        title = b.get("title")
        head_html = f'<h3>{_esc(title)}</h3>' if title else ""
        return f'{head_html}<table class="data"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
    if t == "photo_grid":
        items = b.get("items") or []
        cards = ""
        for it in items:
            caption = _esc(it.get("caption") or "")
            cards += f'<figure class="ph"><div class="ph-box">{caption}</div>' \
                     f'<figcaption>{caption}</figcaption></figure>'
        return f'<div class="photo-grid">{cards}</div>'
    if t == "signature":
        left = "".join(f"<div><span>{_esc(k)}:</span> {_esc(v)}</div>" for k, v in b.get("left", []))
        right = "".join(f"<div><span>{_esc(k)}:</span> {_esc(v)}</div>" for k, v in b.get("right", []))
        return f'<div class="sig"><div class="sig-col">{left}<div class="line"></div></div>' \
               f'<div class="sig-col">{right}<div class="line"></div></div></div>'
    return ""


def _footer_html(case: DiagnosticCase) -> str:
    return f'<div class="page-end"></div>'


def _html_doc(title: str, body: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{_esc(title)}</title>
<style>
  :root {{ --ink:#111; --muted:#666; --line:#ccc; --bg:#fff; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
         color: var(--ink); background: var(--bg); margin: 0;
         font-size: 11pt; line-height: 1.45; }}
  .page {{ max-width: 8.5in; margin: 0 auto; padding: 0.6in 0.6in; }}
  .cover {{ text-align: left; padding: 0.4in 0 0.3in; border-bottom: 2px solid var(--ink); }}
  .brand {{ font-size: 20pt; font-weight: 800; letter-spacing: 0.02em; }}
  .brand-sub {{ font-size: 9pt; letter-spacing: 0.14em; text-transform: uppercase;
                color: var(--muted); margin-top: 2px; }}
  h1 {{ font-size: 16pt; margin: 18px 0 6px; letter-spacing: 0.01em; }}
  h2.sec {{ font-size: 13pt; margin: 22px 0 8px; padding-bottom: 4px;
            border-bottom: 1px solid var(--line); letter-spacing: 0.02em;
            text-transform: uppercase; }}
  h3 {{ font-size: 10.5pt; margin: 12px 0 6px; color: #333; }}
  .cover-meta {{ font-size: 10pt; margin-top: 12px; }}
  .cover-meta div {{ margin-bottom: 3px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 6px 0 12px;
           font-size: 9.5pt; page-break-inside: auto; }}
  table th, table td {{ border: 1px solid var(--line); padding: 5px 7px;
                        vertical-align: top; text-align: left; }}
  table.kv th {{ width: 30%; background: #f3f3f3; font-weight: 600; }}
  table.data thead th {{ background: #f3f3f3; font-weight: 600; }}
  table.data thead {{ display: table-header-group; }}
  table.data tr {{ page-break-inside: avoid; }}
  .warn {{ background: #fff7e0; border-left: 3px solid #d9a400; padding: 6px 10px;
           font-size: 9.5pt; margin: 6px 0 12px; }}
  .empty {{ color: var(--muted); font-style: italic; }}
  .photo-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
  .ph {{ margin: 0; }}
  .ph-box {{ border: 1px solid var(--line); height: 1.6in; display: flex;
             align-items: center; justify-content: center; font-size: 8.5pt;
             color: var(--muted); background: #fafafa; }}
  .ph figcaption {{ font-size: 8.5pt; color: var(--muted); margin-top: 4px; }}
  .sig {{ display: flex; gap: 40px; margin-top: 30px; }}
  .sig-col {{ flex: 1; }}
  .sig-col span {{ color: var(--muted); }}
  .line {{ border-bottom: 1px solid var(--ink); height: 30px; margin-top: 8px; }}
  .page-break {{ page-break-after: always; height: 0; }}
  @media print {{
    @page {{ size: Letter; margin: 0.55in; }}
    body {{ font-size: 10pt; }}
    .page {{ padding: 0; max-width: none; }}
  }}
</style></head><body><div class="page">{body}</div></body></html>"""


# ================================================================== PDF
def generate_pdf(case: DiagnosticCase, section_keys: list[str],
                 out_path: Path, options: dict | None = None) -> Path:
    """Render a clean, print-ready PDF using fpdf2."""
    from fpdf import FPDF

    options = options or {}
    title = options.get("title") or CONFIG.report_title
    include_private = options.get("include_private", False)

    pdf = FPDF(orientation="P", unit="pt", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=54)
    pdf.add_page()

    def h1(text):
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 24, text, ln=1)

    def h2(text):
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 18, text.upper(), ln=1)
        pdf.set_draw_color(180)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(4)

    def h3(text):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 14, text, ln=1)

    def p(text, size=9.5, muted=False):
        pdf.set_font("Helvetica", "", size)
        if muted:
            pdf.set_text_color(110)
        pdf.multi_cell(0, 12, text)
        pdf.set_text_color(0)

    # Cover
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 26, CONFIG.name, ln=1)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 12, CONFIG.subtitle.upper(), ln=1)
    pdf.ln(10)
    h1(title)
    pdf.ln(4)
    v = case.vehicle
    cover_rows = [
        ("Vehicle", v.title),
        ("Case", case.case_number),
        ("VIN", v.vin or "—"),
        ("Mileage", f"{v.mileage:,} {CONFIG.mileage_unit}" if v.mileage else "—"),
        ("Date", datetime.now(timezone.utc).strftime("%B %d, %Y")),
        ("Technician", CONFIG.technician),
    ]
    for k, val in cover_rows:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 16, f"{k}:", border=0)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 16, str(val), border=0, ln=1)
    pdf.add_page()

    for key in section_keys:
        entry = SECTION_REGISTRY.get(key)
        if not entry:
            continue
        if key == "reflection" and not include_private:
            continue
        _, fn = entry
        try:
            blocks = fn(case)
        except Exception:
            continue
        for b in blocks:
            t = b["type"]
            if t == "heading":
                h2(b["text"])
            elif t == "paragraph":
                p(b["text"])
            elif t == "warning":
                pdf.set_fill_color(255, 247, 224)
                pdf.set_text_color(120, 90, 0)
                p("⚠ " + b["text"], muted=False)
                pdf.set_text_color(0)
                pdf.set_fill_color(255)
            elif t == "divider":
                pdf.ln(6)
                pdf.set_draw_color(200)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
                pdf.ln(6)
            elif t == "kv":
                if b.get("title"):
                    h3(b["title"])
                for k, val in b.get("rows") or []:
                    pdf.set_font("Helvetica", "B", 9)
                    pdf.multi_cell(0, 12, f"{k}:", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("Helvetica", "", 9.5)
                    pdf.multi_cell(0, 12, str(val))
                    pdf.ln(1)
            elif t == "table":
                cols = b.get("columns") or []
                rows = b.get("rows") or []
                if b.get("title"):
                    h3(b["title"])
                if not rows:
                    p("No records.", muted=True)
                    continue
                n = max(1, len(cols))
                if n <= 3:
                    widths = [(pdf.w - pdf.l_margin - pdf.r_margin) / n] * n
                else:
                    first = (pdf.w - pdf.l_margin - pdf.r_margin) * 0.55 / 2
                    rest = ((pdf.w - pdf.l_margin - pdf.r_margin) - first * 2) / (n - 2)
                    widths = [first, first] + [rest] * (n - 2)
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_fill_color(240)
                for c, w in zip(cols, widths):
                    pdf.cell(w, 16, str(c)[:28], border=1, fill=True)
                pdf.ln()
                pdf.set_font("Helvetica", "", 8)
                for r in rows:
                    for c, w in zip(cols, widths):
                        txt = str(r.get(c, "") or "")[:60]
                        pdf.cell(w, 14, txt, border=1)
                    pdf.ln()
                pdf.ln(2)
            elif t == "signature":
                pdf.ln(20)
                y = pdf.get_y()
                for i, col in enumerate(("left", "right")):
                    x = pdf.l_margin + i * (pdf.w - pdf.l_margin - pdf.r_margin) / 2
                    pdf.set_xy(x, y)
                    pdf.set_font("Helvetica", "", 9)
                    for k, val in b.get(col, []):
                        pdf.set_x(x)
                        pdf.cell(200, 14, f"{k}: {val}", ln=1)
                    pdf.set_x(x)
                    pdf.line(x, pdf.get_y() + 6, x + 180, pdf.get_y() + 6)

    # Footer on every page
    total = pdf.pages_count
    for i in range(1, total + 1):
        pdf.page = i
        pdf.set_y(-30)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(120)
        pdf.cell(0, 10, f"{CONFIG.footer} · Case {case.case_number} · Page {i} of {total}",
                 align="C")
        pdf.set_text_color(0)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path
