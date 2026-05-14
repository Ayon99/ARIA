from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from simulator.log_generator import generate_anomaly, get_user_baseline
from agent.investigator import investigate
from database.db import init_db, save_incident, get_all_incidents
import asyncio
import json

app = FastAPI(title="ARIA - Autonomous Risk Investigation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections = []

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ARIA is running"}

@app.get("/investigate/{attack_type}")
async def investigate_anomaly(attack_type: str, user_id: str = "user_123"):
    anomaly = generate_anomaly(attack_type, user_id)
    baseline = get_user_baseline(user_id)
    result = investigate(anomaly, baseline)
    save_incident(anomaly, result)
    
    # Broadcast to all connected clients
    incident = {**anomaly, "investigation": result}
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(incident, default=str))
        except:
            pass
    
    return {"anomaly": anomaly, "investigation": result}

@app.get("/incidents")
def list_incidents():
    return get_all_incidents()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except:
        active_connections.remove(websocket)