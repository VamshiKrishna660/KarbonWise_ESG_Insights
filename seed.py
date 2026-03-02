"""
Seed script: inserts 2 sample ESG records directly (no LLM needed).
Run: python seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

SAMPLE_DATA = [
    {
        "document": {"filename": "acme_esg_2023.pdf", "file_type": "pdf"},
        "record": {
            "company_name": "Acme Corp",
            "report_year": 2023,
            "emissions_co2_tonnes": 12500.0,
            "energy_usage_mwh": 48000.0,
            "water_usage_m3": 320000.0,
            "sustainability_targets": "Achieve net-zero emissions by 2040; reduce water usage by 20% by 2026.",
            "raw_text_excerpt": "Acme Corp 2023 Sustainability Report. Total GHG emissions: 12,500 tCO2e. Energy consumption: 48,000 MWh. Water withdrawal: 320,000 m3.",
            "confidence_score": 0.95,
        },
    },
    {
        "document": {"filename": "greentec_esg_2022.xlsx", "file_type": "xlsx"},
        "record": {
            "company_name": "GreenTec Industries",
            "report_year": 2022,
            "emissions_co2_tonnes": 7800.0,
            "energy_usage_mwh": 31500.0,
            "water_usage_m3": 185000.0,
            "sustainability_targets": "50% renewable energy by 2025; reduce Scope 3 emissions by 30% by 2030.",
            "raw_text_excerpt": "GreenTec Industries Environmental Report 2022. Scope 1+2 emissions: 7,800 tonnes CO2. Total energy: 31,500 MWh. Water used: 185,000 cubic metres.",
            "confidence_score": 0.91,
        },
    },
]


def seed():
    db = SessionLocal()
    try:
        for entry in SAMPLE_DATA:
            # Skip if already seeded
            existing = db.query(models.Document).filter_by(filename=entry["document"]["filename"]).first()
            if existing:
                print(f"  [SKIP] {entry['document']['filename']} already exists.")
                continue

            doc = models.Document(**entry["document"])
            db.add(doc)
            db.flush()

            rec = models.SustainabilityRecord(document_id=doc.id, **entry["record"])
            db.add(rec)
            print(f"  [INSERT] {entry['document']['filename']} → record for {entry['record']['company_name']}")

        db.commit()
        print("\n✅ Seeding complete.")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
