"""Schema definitions — single source of truth for form sections,
vehicle systems, test types, and report section catalogue."""
from __future__ import annotations

REQ_LABEL = {"R": "REQUIRED", "IA": "IF APPLICABLE", "O": "OPTIONAL"}

VEHICLE_SYSTEMS = [
    "Power", "Ground", "Battery/charging", "Starting", "Fuel", "Ignition",
    "Air/intake", "Engine mechanical", "Cooling", "Lubrication",
    "Transmission", "ABS/brakes", "Steering", "Suspension", "HVAC",
    "Lighting", "Body", "Network/CAN", "Immobilizer/security",
    "Sensors/actuators", "Control modules", "Other",
]

TEST_RESULTS = ["pass", "fail", "inconclusive", "n/a"]

DTC_STATUSES = ["present", "pending", "stored", "history", "cleared"]

HYPOTHESIS_STATUSES = [
    "suspected", "testing", "supported", "confirmed", "ruled_out", "inconclusive",
]

CONFIDENCE_LEVELS = [
    "Confirmed", "Highly supported", "Probable", "Inconclusive", "Not confirmed",
]

FINAL_STATUSES = [
    "Repaired / verified", "Repaired / monitoring",
    "Diagnosed / repair pending", "Diagnosed / parts pending",
    "Diagnosis inconclusive", "Further testing required",
    "Customer declined repair", "Vehicle unsafe to operate",
    "Requires specialist / dealer-level equipment",
]

CASE_CLASSIFICATIONS = [
    "No-start", "Crank/no-start", "Misfire", "Electrical", "Check-engine light",
    "ABS", "Transmission", "HVAC", "Starting/charging", "Network/CAN",
    "Mechanical", "Intermittent fault", "Preventative maintenance",
    "General repair", "Difficult diagnosis",
]

CASE_TAGS = [
    "Solved", "Important", "Learning case", "Electrical", "No-start",
    "Driveability", "Network/CAN", "Cooling", "HVAC", "Brakes",
    "Suspension", "Maintenance", "Difficult diagnosis",
]


# ------------------------------------------------------------------ sections
# Each section: id, title, subtitle (optional), fields[]
# Field types: text, number, date, text_area, select, multi, check, table

VEHICLE_ID = {
    "id": "vehicle_id",
    "title": "1. Vehicle Identification",
    "fields": [
        {"key": "date", "label": "Date", "type": "text", "req": "R"},
        {"key": "technician", "label": "Technician", "type": "text", "req": "R"},
        {"key": "owner_name", "label": "Owner / Customer", "type": "text", "req": "R"},
        {"key": "ro_number", "label": "RO / Work-order #", "type": "text", "req": "IA"},
        {"key": "case_number", "label": "Diagnostic case #", "type": "text", "req": "R"},
        {"key": "vin", "label": "VIN", "type": "text", "req": "R"},
        {"key": "year", "label": "Year", "type": "number", "req": "R"},
        {"key": "make", "label": "Make", "type": "text", "req": "R"},
        {"key": "model", "label": "Model", "type": "text", "req": "R"},
        {"key": "trim", "label": "Trim", "type": "text", "req": "IA"},
        {"key": "engine", "label": "Engine", "type": "text", "req": "R"},
        {"key": "engine_code", "label": "Engine code", "type": "text", "req": "IA"},
        {"key": "transmission", "label": "Transmission", "type": "text", "req": "IA"},
        {"key": "drivetrain", "label": "Drivetrain", "type": "select", "req": "IA",
         "options": ["", "FWD", "RWD", "AWD", "4WD"]},
        {"key": "mileage", "label": "Mileage", "type": "text", "req": "R"},
        {"key": "plate", "label": "License plate", "type": "text", "req": "IA"},
        {"key": "location", "label": "Vehicle location", "type": "text", "req": "IA"},
        {"key": "fuel_level", "label": "Fuel level", "type": "text", "req": "IA"},
        {"key": "battery", "label": "Battery condition / voltage", "type": "text", "req": "IA"},
        {"key": "arrival", "label": "Arrival condition", "type": "multi", "req": "R",
         "options": ["Drivable", "Cranks-no-start", "No-crank", "Towed",
                     "Pushed-in", "Other"]},
        {"key": "mods", "label": "Modifications / aftermarket equipment", "type": "multi", "req": "IA",
         "options": ["None observed", "Aftermarket alarm", "Aftermarket radio", "Remote start",
                     "Tuning/programmer", "Aftermarket lighting", "Lift/suspension",
                     "Wheels/tires", "Electrical add-ons", "Other"]},
        {"key": "mods_notes", "label": "Modification notes", "type": "text_area", "req": "O"},
    ],
}

COMPLAINT = {
    "id": "complaint",
    "title": "2. Customer Complaint / Initial Concern",
    "subtitle": "Record as reported, without interpretation.",
    "fields": [
        {"key": "statement", "label": "Customer statement", "type": "text_area", "req": "R"},
        {"key": "started", "label": "When did the problem start?", "type": "text", "req": "IA"},
        {"key": "conditions", "label": "Conditions under which it occurs", "type": "text_area", "req": "IA"},
        {"key": "frequency", "label": "Frequency", "type": "select", "req": "IA",
         "options": ["", "Constant", "Intermittent", "Once", "Unknown"]},
        {"key": "recent_repairs", "label": "Recent repairs", "type": "text_area", "req": "IA"},
        {"key": "recent_parts", "label": "Recent parts replacement", "type": "text_area", "req": "IA"},
        {"key": "accident", "label": "Accident / water exposure", "type": "text", "req": "IA"},
        {"key": "weather", "label": "Weather / temperature conditions", "type": "text", "req": "IA"},
        {"key": "tried", "label": "What has the customer already tried?", "type": "text_area", "req": "IA"},
        {"key": "prior_tech", "label": "Another technician already diagnosed/repaired?",
         "type": "text_area", "req": "IA"},
    ],
}

INITIAL_CONDITION = {
    "id": "initial_condition",
    "title": "3. Initial Vehicle Condition",
    "subtitle": "Documented BEFORE touching anything.",
    "fields": [
        {"key": "doc_before", "label": "Condition documented before repair/diagnosis",
         "type": "check", "req": "R"},
        {"key": "exterior", "label": "Exterior condition", "type": "text_area", "req": "IA"},
        {"key": "engine_bay", "label": "Engine-bay condition", "type": "text_area", "req": "IA"},
        {"key": "fluid_leaks", "label": "Fluid leaks", "type": "multi", "req": "IA",
         "options": ["None", "Oil", "Coolant", "ATF", "Power steering", "Fuel",
                     "Brake", "Other"]},
        {"key": "fluid_levels", "label": "Fluid levels", "type": "text_area", "req": "IA"},
        {"key": "wiring", "label": "Wiring / connectors", "type": "text_area", "req": "IA"},
        {"key": "grounds", "label": "Grounds", "type": "text", "req": "IA"},
        {"key": "battery_term", "label": "Battery terminals", "type": "text", "req": "IA"},
        {"key": "fuses", "label": "Fuses / relays", "type": "text", "req": "IA"},
        {"key": "damage", "label": "Visible damage", "type": "text_area", "req": "IA"},
        {"key": "corrosion", "label": "Corrosion", "type": "text", "req": "IA"},
        {"key": "rodent_water", "label": "Rodent / water intrusion", "type": "multi", "req": "IA",
         "options": ["None", "Rodent", "Water", "Both"]},
        {"key": "smells", "label": "Unusual smells", "type": "text", "req": "IA"},
        {"key": "noises", "label": "Unusual noises", "type": "text", "req": "IA"},
        {"key": "warning_lights", "label": "Warning lights (dash)", "type": "text", "req": "IA"},
        {"key": "cluster", "label": "Gauge / cluster behavior", "type": "text", "req": "IA"},
        {"key": "starting", "label": "Starting condition", "type": "text", "req": "IA"},
        {"key": "running", "label": "Running condition", "type": "text", "req": "IA"},
    ],
}

SCAN_DATA = {
    "id": "scan_data",
    "title": "4. Initial Diagnostic Data (Scan Tool)",
    "fields": [
        {"key": "scan_tool", "label": "Scan tool used", "type": "text", "req": "R"},
        {"key": "software", "label": "Software / version", "type": "text", "req": "IA"},
        {"key": "timestamp", "label": "Date / time", "type": "text", "req": "R"},
        {"key": "comm_status", "label": "Vehicle communication status", "type": "select", "req": "R",
         "options": ["", "OK", "Intermittent", "No comm"]},
        {"key": "modules", "label": "Modules scanned", "type": "text_area", "req": "IA"},
        {"key": "system_voltage", "label": "Battery / system voltage", "type": "text", "req": "IA"},
        {"key": "no_dtcs", "label": "No DTCs present", "type": "check", "req": "O"},
        {"key": "ucodes", "label": "U-codes / network present", "type": "check", "req": "O"},
        {"key": "comm_fault", "label": "Communication fault present", "type": "check", "req": "O"},
        {"key": "live_data", "label": "Live-data observations", "type": "text_area", "req": "IA"},
        {"key": "readiness", "label": "Readiness monitors", "type": "text_area", "req": "IA"},
        {"key": "module_info", "label": "Relevant module information", "type": "text_area", "req": "IA"},
    ],
}

SYMPTOMS = {
    "id": "symptoms",
    "title": "5. Symptom Reproduction",
    "fields": [
        {"key": "reproduced", "label": "Complaint reproduced", "type": "select", "req": "R",
         "options": ["", "YES", "NO", "INTERMITTENT"]},
        {"key": "engine_temp", "label": "Engine temperature", "type": "text", "req": "IA"},
        {"key": "ambient", "label": "Ambient temperature", "type": "text", "req": "IA"},
        {"key": "speed", "label": "Vehicle speed", "type": "text", "req": "IA"},
        {"key": "rpm", "label": "RPM", "type": "text", "req": "IA"},
        {"key": "load", "label": "Load", "type": "text", "req": "IA"},
        {"key": "gear", "label": "Gear", "type": "text", "req": "IA"},
        {"key": "electrical", "label": "Electrical load", "type": "text", "req": "IA"},
        {"key": "road", "label": "Road conditions", "type": "text", "req": "IA"},
        {"key": "observed", "label": "Exact symptom observed", "type": "text_area", "req": "R"},
        {"key": "frequency", "label": "Frequency", "type": "text", "req": "IA"},
        {"key": "duration", "label": "Duration", "type": "text", "req": "IA"},
        {"key": "unable_repro", "label": "If unable to reproduce — how tested and what observed",
         "type": "text_area", "req": "IA"},
    ],
}

PLAN = {
    "id": "plan",
    "title": "6. Diagnostic Plan",
    "subtitle": "Written BEFORE performing tests.",
    "fields": [
        {"key": "systems", "label": "Suspected systems", "type": "multi", "req": "R",
         "options": VEHICLE_SYSTEMS},
        {"key": "hypothesis", "label": "Initial hypothesis", "type": "text_area", "req": "R"},
        {"key": "evidence_for", "label": "Evidence supporting hypothesis", "type": "text_area", "req": "R"},
        {"key": "evidence_against", "label": "Evidence against hypothesis", "type": "text_area", "req": "IA"},
        {"key": "next_test", "label": "Next test", "type": "text", "req": "R"},
        {"key": "expected", "label": "Expected result", "type": "text", "req": "R"},
        {"key": "actual", "label": "Actual result", "type": "text", "req": "IA"},
    ],
}

WIRING = {
    "id": "wiring",
    "title": "9. Wiring / Electrical Diagnostics",
    "fields": [
        {"key": "diagram_ref", "label": "Wiring diagram reference", "type": "text", "req": "IA"},
        {"key": "circuit", "label": "Circuit / component", "type": "text", "req": "IA"},
        {"key": "power_source", "label": "Power source", "type": "text", "req": "IA"},
        {"key": "fuse", "label": "Fuse", "type": "text", "req": "IA"},
        {"key": "relay", "label": "Relay", "type": "text", "req": "IA"},
        {"key": "ground", "label": "Ground", "type": "text", "req": "IA"},
        {"key": "connector", "label": "Connector", "type": "text", "req": "IA"},
        {"key": "pin", "label": "Pin number", "type": "text", "req": "IA"},
        {"key": "wire_color", "label": "Wire color", "type": "text", "req": "IA"},
        {"key": "backprobe", "label": "Back-probing / connector-pin notes", "type": "text_area", "req": "IA"},
    ],
}

ROOT_CAUSE = {
    "id": "root_cause",
    "title": "11. Root-Cause Analysis",
    "fields": [
        {"key": "symptom", "label": "Symptom — What happened?", "type": "text_area", "req": "R"},
        {"key": "failure", "label": "Failure — What actually failed?", "type": "text_area", "req": "R"},
        {"key": "root_cause", "label": "Root cause — Why did it fail?", "type": "text_area", "req": "R"},
        {"key": "contributing", "label": "Contributing factors", "type": "text_area", "req": "IA"},
        {"key": "evidence", "label": "Objective evidence", "type": "text_area", "req": "R"},
        {"key": "confidence", "label": "Confidence", "type": "select", "req": "R",
         "options": [""] + CONFIDENCE_LEVELS},
    ],
}

REPAIR_NOTES = {
    "id": "repair_notes",
    "title": "12. Repair / Corrective Action",
    "fields": [
        {"key": "repair_performed", "label": "Repair performed", "type": "text_area", "req": "R"},
        {"key": "parts_replaced", "label": "Parts replaced", "type": "text_area", "req": "IA"},
        {"key": "part_numbers", "label": "Part numbers", "type": "text", "req": "IA"},
        {"key": "fluids", "label": "Fluids / materials used", "type": "text", "req": "IA"},
        {"key": "wiring_repair", "label": "Wiring repaired", "type": "text", "req": "IA"},
        {"key": "connector_repair", "label": "Connectors repaired", "type": "text", "req": "IA"},
        {"key": "programming", "label": "Software / programming", "type": "text", "req": "IA"},
        {"key": "calibration", "label": "Calibration / relearn", "type": "text", "req": "IA"},
        {"key": "torque", "label": "Torque specifications", "type": "text", "req": "IA"},
        {"key": "special_proc", "label": "Special procedures", "type": "text_area", "req": "IA"},
        {"key": "labor_time", "label": "Labor time (hrs)", "type": "text", "req": "IA"},
        {"key": "before_measure", "label": "Before measurements", "type": "text_area", "req": "IA"},
        {"key": "after_measure", "label": "After measurements", "type": "text_area", "req": "IA"},
        {"key": "tech_notes", "label": "Technician notes", "type": "text_area", "req": "O"},
        {"key": "why", "label": "Why this repair was performed", "type": "text_area", "req": "R"},
    ],
}

VERIFICATION = {
    "id": "verification",
    "title": "13. Post-Repair Verification",
    "subtitle": "Mandatory.",
    "fields": [
        {"key": "repair_complete", "label": "Repair completed", "type": "check", "req": "R"},
        {"key": "restarted", "label": "Vehicle restarted", "type": "check", "req": "R"},
        {"key": "repro_after", "label": "Symptom reproduced after repair", "type": "select", "req": "R",
         "options": ["", "No", "Yes", "Intermittent"]},
        {"key": "dtc_cleared", "label": "DTCs cleared", "type": "check", "req": "R"},
        {"key": "dtc_returned", "label": "DTCs returned", "type": "text", "req": "R"},
        {"key": "road_test", "label": "Road test completed", "type": "check", "req": "R"},
        {"key": "scan_after", "label": "Scan performed after repair", "type": "check", "req": "R"},
        {"key": "live_after", "label": "Live data checked", "type": "check", "req": "IA"},
        {"key": "system_confirmed", "label": "System operation confirmed", "type": "check", "req": "R"},
        {"key": "no_new_faults", "label": "No new faults created", "type": "check", "req": "R"},
        {"key": "outcome", "label": "Outcome", "type": "select", "req": "R",
         "options": ["", "Repair successful", "Partially successful", "Unsuccessful",
                     "Further diagnosis required"]},
        {"key": "before", "label": "Before-repair condition", "type": "text_area", "req": "R"},
        {"key": "after", "label": "After-repair condition", "type": "text_area", "req": "R"},
        {"key": "evidence_fixed", "label": "Evidence the repair fixed the problem",
         "type": "text_area", "req": "R"},
    ],
}

REMAINING = {
    "id": "remaining",
    "title": "14. Remaining Issues",
    "subtitle": "Unresolved issues must not disappear because the primary complaint was repaired.",
    "fields": [
        {"key": "issues", "label": "Open issues", "type": "table", "req": "IA",
         "columns": ["Issue", "Severity", "Safety-relevant?", "Status", "Next step",
                     "Parts needed", "Additional testing", "Priority"]},
    ],
}

SAFETY = {
    "id": "safety",
    "title": "15. Safety / Roadworthiness",
    "fields": [
        {"key": "safety_items", "label": "Safety areas", "type": "table", "req": "IA",
         "columns": ["Area", "Finding", "Diagnostic vs Safety-critical"]},
    ],
}

MAINTENANCE_OBS = {
    "id": "maintenance_obs",
    "title": "16. Maintenance / Additional Observations",
    "subtitle": "Findings unrelated to the primary complaint.",
    "fields": [
        {"key": "obs", "label": "Additional observations", "type": "table", "req": "O",
         "columns": ["Item", "Observation", "Recommended action"]},
    ],
}

SUMMARY = {
    "id": "summary",
    "title": "17. Final Diagnostic Summary",
    "fields": [
        {"key": "orig_complaint", "label": "Original complaint", "type": "text_area", "req": "R"},
        {"key": "verified_symptom", "label": "Verified symptom", "type": "text_area", "req": "R"},
        {"key": "confirmed_cause", "label": "Confirmed cause", "type": "text_area", "req": "R"},
        {"key": "evidence", "label": "Diagnostic evidence", "type": "text_area", "req": "R"},
        {"key": "repair_done", "label": "Repair performed", "type": "text_area", "req": "R"},
        {"key": "post_verify", "label": "Post-repair verification", "type": "text_area", "req": "R"},
        {"key": "remaining_conc", "label": "Remaining concerns", "type": "text_area", "req": "IA"},
        {"key": "next_action", "label": "Recommended next action", "type": "text_area", "req": "IA"},
        {"key": "final_status", "label": "Final vehicle status", "type": "text", "req": "R"},
    ],
}

REFLECTION = {
    "id": "reflection",
    "title": "18. Technician Learning / Reflection",
    "subtitle": "Private — never included in customer-facing reports.",
    "fields": [
        {"key": "learned", "label": "What I learned", "type": "text_area", "req": "O"},
        {"key": "best_test", "label": "Most useful test", "type": "text", "req": "O"},
        {"key": "wrong_assume", "label": "Assumption that was wrong", "type": "text_area", "req": "O"},
        {"key": "initial_susp", "label": "What I initially suspected", "type": "text_area", "req": "O"},
        {"key": "changed_mind", "label": "What changed my mind", "type": "text_area", "req": "O"},
        {"key": "first_next", "label": "What I would test first next time", "type": "text_area", "req": "O"},
        {"key": "tool_learned", "label": "Tool / procedure learned", "type": "text", "req": "O"},
        {"key": "diagram_used", "label": "Wiring diagram section used", "type": "text", "req": "O"},
        {"key": "principle", "label": "Diagnostic principle involved", "type": "text", "req": "O"},
        {"key": "mistakes", "label": "Mistakes made", "type": "text_area", "req": "O"},
        {"key": "differently", "label": "What I would do differently", "type": "text_area", "req": "O"},
    ],
}

COSTS = {
    "id": "costs",
    "title": "21. Parts & Cost Tracking",
    "fields": [
        {"key": "cost_parts", "label": "Parts", "type": "table", "req": "O",
         "columns": ["Part", "Part #", "Brand", "Qty", "Cost", "Supplier", "Warranty"]},
        {"key": "cost_totals", "label": "Totals", "type": "table", "req": "O",
         "columns": ["Category", "Amount"]},
    ],
}

FINAL_STATUS = {
    "id": "final_status",
    "title": "22. Final Status",
    "fields": [
        {"key": "status", "label": "Final classification", "type": "multi", "req": "R",
         "options": FINAL_STATUSES},
    ],
}


# Sections stored as JSON on the case, in display order
NARRATIVE_SECTIONS = [
    COMPLAINT, INITIAL_CONDITION, SCAN_DATA, SYMPTOMS, PLAN, WIRING,
    ROOT_CAUSE, REPAIR_NOTES, VERIFICATION, REMAINING, SAFETY,
    MAINTENANCE_OBS, SUMMARY, REFLECTION, COSTS, FINAL_STATUS,
]

# Mapping section id -> attribute name on DiagnosticCase
SECTION_TO_ATTR = {
    "complaint": "complaint",
    "initial_condition": "initial_condition",
    "scan_data": "scan_data",
    "symptoms": "symptoms",
    "plan": "plan",
    "wiring": "wiring",
    "root_cause": "root_cause",
    "repair_notes": "repair_notes",
    "verification": "verification",
    "remaining": "remaining",
    "safety": "safety",
    "maintenance_obs": "maintenance_obs",
    "summary": "summary",
    "reflection": "reflection",
    "costs": "costs",
    "final_status": "final_status",
}
