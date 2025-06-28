import requests
import random
import uuid
from datetime import datetime

API_URL = "http://localhost:8000/survey"

PILOT_TAGS = ["SmartTicketing", "SmartEnergy", "Healthcare", "Manufacturing"]
APP_VERSIONS = ["1.0.0", "1.2.0", "2.0.1", "2.1.0", "2.2.0"]
AI_MODEL_VERSIONS = ["v1.0.0", "v1.1.5", "v2.0.0"]

def random_sus():
    return {f"sus_q{i}": random.randint(1, 5) for i in range(1, 11)}

def random_ethics():
    return {
        "q_fairness": random.randint(1, 5),
        "q_transparency": random.randint(1, 5),
        "q_privacy": random.randint(1, 5),
        "q_accountability": random.randint(1, 5),
        "q_trust": random.randint(1, 5)
    }

def random_domain_specific(pilot):
    if pilot == "SmartTicketing":
        return {
            "smart_ticketing_q1": random.randint(1, 5),
            "smart_ticketing_q2": random.randint(1, 5)
        }
    elif pilot == "SmartEnergy":
        return {
            "smart_energy_q1": random.randint(1, 5),
            "smart_energy_q2": random.randint(1, 5)
        }
    else:
        return {
            "healthcare_q1": random.randint(1, 5)
        }

def generate_payload():
    pilot = random.choice(PILOT_TAGS)
    payload = {
        "survey_id": str(uuid.uuid4()),
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.utcnow().isoformat(),
        "pilot_tag": pilot,
        "app_version": random.choice(APP_VERSIONS),
        "ai_model_version": random.choice(AI_MODEL_VERSIONS),
        "tam_sus_responses": random_sus(),
        "ethics_responses": random_ethics(),
        "domain_specific": random_domain_specific(pilot)
    }
    return payload

def submit_sample_data(n=10):
    for i in range(n):
        response = requests.post(API_URL, json=generate_payload())
        print(f"[{i+1}] Status: {response.status_code} | Response: {response.json()}")

if __name__ == "__main__":
    submit_sample_data(n=100)