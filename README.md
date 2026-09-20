# SURAJ'S GARAGE
### Automotive Diagnostic & Service Journal — Master Professional Build v2.1

A professional, extensible automotive diagnostic and service log built on Streamlit.
Schema-driven forms, structured diagnostic records, a full Report Builder /
Print Studio, and complete case-vehicle history.

## Features

- **Schema-driven forms** — one source of truth for all 23 diagnostic sections
- **Relational + JSON hybrid** — tests, measurements, DTCs, hypotheses, repairs, attachments are proper tables; narrative sections stay flexible JSON
- **Professional Report Builder** — block-based HTML + PDF generation with templates + privacy controls
- **Safe attachments** — UUID-prefixed filenames, size limits, controlled directories
- **Deep linking** — open any case with `?case=SG-YYYYMMDD-###`
- **Full search** across vehicles, cases, DTCs, tests, measurements, repairs
- **Timeline & learning reflection** (private — excluded from customer reports)
- **Dark professional theme**

## Install

```bash
pip install -r requirements.txt
```

Copy the secrets example and set your password hash:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
python -c "import streamlit_authenticator as stauth; print(stauth.Hasher.hash('your-password'))"
```

Paste the `$2b$12$...` hash into `.streamlit/secrets.toml`.

## Initialize

```bash
python init_db.py
```

## Run

```bash
streamlit run app.py
```

Browser opens at http://localhost:8501.

## Project Structure

```
surajs-garage/
├── app.py                 # Entry point + routing + deep links
├── init_db.py             # DB init + sample seed
├── config.py              # Branding, paths, theme, case_url_base
├── db.py                  # SQLAlchemy models (local timestamps)
├── auth.py                # Authentication
├── storage.py             # Safe file uploads
├── schemas.py             # Form sections (single source of truth)
├── form_renderer.py       # Schema → Streamlit widgets + clean tables
├── services.py            # All CRUD
├── reports.py             # Report engine (HTML + PDF)
├── views/                 # Pages
└── data/                  # SQLite + attachments + reports + backups
```

## Extending

- **Add a form field** → edit the section in `schemas.py`
- **Add a vehicle system** → append to `VEHICLE_SYSTEMS`
- **Add a report section** → register in `reports.SECTION_REGISTRY`
- **Add a report template** → add to `reports.BUILTIN_TEMPLATES` or use the UI

## Notes

- Local time is used for all new timestamps.
- Customer-facing reports never include the technician reflection section.
- Export (Settings) is a JSON snapshot only — it does not include attachment binaries or generated PDFs.

## License

Private use — Suraj Thapa / SURAJ'S GARAGE
