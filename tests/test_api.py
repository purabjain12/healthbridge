import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "HealthBridge Hybrid API"

def test_hybrid_endpoint_success():
    payload = {
        "patient_id": "TEST001",
        "payer": "Aetna",
        "procedure_cpt": "72148",
        "clinical_notes": "Chronic lower back pain for 14 weeks. Failed PT and NSAIDs. No red flags."
    }
    response = client.post("/api/v2/prior-auth/hybrid", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "hybrid_decision" in data
    assert "final_recommendation" in data["hybrid_decision"]

def test_hybrid_endpoint_validation_fail():
    payload = {
        "patient_id": "AB",  # too short (min 3)
        "payer": "Aetna",
        "procedure_cpt": "123",  # invalid CPT (must be 5 digits)
        "clinical_notes": "Short"  # too short
    }
    response = client.post("/api/v2/prior-auth/hybrid", json=payload)
    assert response.status_code == 422  # FastAPI validation error