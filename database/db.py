import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS incidents (
                id SERIAL PRIMARY KEY,
                event_id TEXT,
                user_id TEXT,
                attack_type TEXT,
                mitre_technique TEXT,
                severity TEXT,
                confidence FLOAT,
                attack_pattern TEXT,
                is_false_positive BOOLEAN,
                report TEXT,
                anomaly_json TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
    print("Database ready")

def save_incident(anomaly, result):
    import json
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO incidents (
                event_id, user_id, attack_type, mitre_technique,
                severity, confidence, attack_pattern, is_false_positive,
                report, anomaly_json
            ) VALUES (
                :event_id, :user_id, :attack_type, :mitre_technique,
                :severity, :confidence, :attack_pattern, :is_false_positive,
                :report, :anomaly_json
            )
        """), {
            "event_id": anomaly["event_id"],
            "user_id": anomaly["user_id"],
            "attack_type": anomaly["attack_type"],
            "mitre_technique": anomaly["mitre_technique"],
            "severity": result["severity"],
            "confidence": result["confidence"],
            "attack_pattern": result["attack_pattern"],
            "is_false_positive": result["is_false_positive"],
            "report": result["report"],
            "anomaly_json": json.dumps(anomaly)
        })
        conn.commit()

def get_all_incidents():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT * FROM incidents ORDER BY created_at DESC
        """))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]