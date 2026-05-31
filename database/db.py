import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not set in environment")

# Add pool settings for PostgreSQL
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=3600
)

def init_db():
    """Create tables on startup"""
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
    print("✅ Database initialized")

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
            SELECT id, event_id, user_id, attack_type, mitre_technique,
                   severity, confidence, attack_pattern, is_false_positive,
                   report, anomaly_json, created_at
            FROM incidents 
            ORDER BY created_at DESC 
            LIMIT 100
        """))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]