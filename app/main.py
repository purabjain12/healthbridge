from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.services.auth_service import process_prior_auth_hybrid
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="HealthBridge Hybrid MVP", version="0.3.0")

class AuthRequest(BaseModel):
    patient_id: str = Field(..., min_length=3, max_length=20)
    payer: str = Field(..., description="Insurance provider (e.g., Aetna, BlueCross)")
    procedure_cpt: str = Field(..., pattern=r"^\d{5}$", description="CPT code")
    clinical_notes: str = Field(..., min_length=10)

class HybridResponse(BaseModel):
    status: str
    patient_id: str
    extracted_features: dict
    rule_engine: dict
    ml_prediction: dict
    hybrid_decision: dict

@app.get("/")
def health_check():
    return {"status": "HealthBridge Hybrid API", "version": "0.3.0"}

@app.post("/api/v2/prior-auth/hybrid", response_model=HybridResponse)
def submit_hybrid_prior_auth(request: AuthRequest):
    result = process_prior_auth_hybrid(
        request.patient_id, request.payer, request.procedure_cpt, request.clinical_notes
    )
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result