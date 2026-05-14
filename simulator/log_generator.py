import random
from datetime import datetime, timedelta
import uuid

LOCATIONS = {
    "normal": [
        {"country": "IN", "city": "Mumbai", "ip": "103.21.244.0"},
        {"country": "IN", "city": "Delhi", "ip": "103.22.100.5"},
    ],
    "anomalous": [
        {"country": "US", "city": "New York", "ip": "192.168.1.1"},
        {"country": "RU", "city": "Moscow", "ip": "185.220.101.5"},
        {"country": "CN", "city": "Beijing", "ip": "1.180.204.0"},
    ]
}

def generate_normal_event(user_id):
    location = random.choice(LOCATIONS["normal"])
    return {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "ip": location["ip"],
        "geo": {"country": location["country"], "city": location["city"]},
        "action": "login_success",
        "device": "Chrome/Windows",
        "session_id": str(uuid.uuid4()),
        "failed_attempts": 0
    }

def generate_anomaly(attack_type, user_id):
    base = generate_normal_event(user_id)
    
    if attack_type == "impossible_travel":
        location = random.choice(LOCATIONS["anomalous"])
        base["geo"] = {"country": location["country"], "city": location["city"]}
        base["ip"] = location["ip"]
        base["attack_type"] = "impossible_travel"
        base["mitre_technique"] = "T1078"

    elif attack_type == "credential_stuffing":
        base["action"] = "login_failed"
        base["failed_attempts"] = random.randint(20, 50)
        base["attack_type"] = "credential_stuffing"
        base["mitre_technique"] = "T1110"

    elif attack_type == "off_hours_access":
        anomalous_time = datetime.utcnow().replace(hour=3, minute=random.randint(0,59))
        base["timestamp"] = anomalous_time.isoformat()
        base["attack_type"] = "off_hours_access"
        base["mitre_technique"] = "T1078.001"

    return base

def get_user_baseline(user_id):
    return {
        "user_id": user_id,
        "typical_location": "Mumbai, India",
        "typical_hours": "09:00 - 18:00 IST",
        "avg_failed_attempts": 0,
        "typical_device": "Chrome/Windows",
        "login_frequency": "2-3 times per day"
    }