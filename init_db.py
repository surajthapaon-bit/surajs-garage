"""Initialize DB and seed a sample case. Run once: python init_db.py"""
from __future__ import annotations

from db import init_db, session_scope
from db import (
    DiagnosticCase, DTC, Hypothesis, Test, TimelineEvent, Vehicle,
)


def main() -> None:
    init_db()
    print("Tables created.")

    with session_scope() as s:
        existing = s.query(Vehicle).filter_by(is_sample=True).first()
        if existing:
            print("Sample already present.")
            return

        v = Vehicle(
            owner="suraj", nickname="Sample · 2017 Cruze",
            year=2017, make="Chevrolet", model="Cruze", trim="LT",
            vin="SAMPLE-VIN-NOT-REAL", engine="1.4L Turbo",
            engine_code="LE2", transmission="6-spd auto", drivetrain="FWD",
            mileage=123456, is_sample=True,
            notes="Sample case — not a real vehicle.",
        )
        s.add(v)
        s.flush()

        c = DiagnosticCase(
            case_number="SG-SAMPLE-001", vehicle_id=v.id,
            title="Crank / no start", status="open",
            classification="No-start",
            complaint={
                "statement": "Cranks, does not fire.",
                "started": "Two days ago",
                "frequency": "Constant",
                "conditions": "Cold start",
            },
        )
        s.add(c)
        s.flush()

        s.add(TimelineEvent(case_id=c.id, kind="case",
                            description="Sample case opened.", auto=True))
        s.add(Test(
            case_id=c.id, system="Ignition",
            component="CKP signal at ECM",
            procedure="Backprobe CKP pins at ECM, crank engine.",
            tool="Oscilloscope", result="fail",
            expected="AC signal present",
            actual="No signal at ECM",
            interpretation="Suspect harness open or sensor.",
            proves="Signal is absent at ECM.",
            rules_out="CKP sensor output — cannot confirm without testing at sensor.",
            next_step="Test wiring continuity from CKP to ECM.",
        ))
        s.add(DTC(
            case_id=c.id, code="P0335", module="ECM", status="present",
            description="Crankshaft Position Sensor A Circuit",
        ))
        s.add(Hypothesis(
            case_id=c.id, label="H1",
            statement="CKP harness open circuit between sensor and ECM.",
            status="supported", confidence=70,
            supporting="No signal at ECM but cranks normally.",
            contradicting="Sensor not yet tested directly.",
        ))

        print("Sample case seeded.")


if __name__ == "__main__":
    main()
