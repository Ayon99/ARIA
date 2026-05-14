from fastapi import FastAPI
from simulator.log_generator import generate_anomaly, get_user_baseline
from agent.investigator import investigate
from database.db import init_db, save_incident, get_all_incidents
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="ARIA - Autonomous Risk Investigation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ARIA is running"}

@app.get("/investigate/{attack_type}")
def investigate_anomaly(attack_type: str, user_id: str = "user_123"):
    anomaly = generate_anomaly(attack_type, user_id)
    baseline = get_user_baseline(user_id)
    result = investigate(anomaly, baseline)
    save_incident(anomaly, result)
    return {
        "anomaly": anomaly,
        "investigation": result
    }

@app.get("/incidents")
def list_incidents():
    return get_all_incidents()
