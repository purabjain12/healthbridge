from app.core.extraction import process_clinical_notes
from app.core.decision_engine import PayerRuleEngine
from app.core.ml_predictor import ml_predictor
import logging

logger = logging.getLogger(__name__)
engine = PayerRuleEngine()

def process_prior_auth_hybrid(patient_id: str, payer: str, procedure_cpt: str, clinical_notes: str):
    logger.info(f"Processing hybrid auth for patient={patient_id}, CPT={procedure_cpt}")
    
    try:
        # 1. Extract clinical features
        extracted = process_clinical_notes(clinical_notes)
        
        # 2. Run Rule Engine
        rule_result = engine.evaluate(
            procedure_cpt=procedure_cpt,
            extracted_duration=extracted["extracted_duration_weeks"],
            conservative_detected=extracted["conservative_care_detected"],
            red_flags_detected=extracted["red_flags_detected"]
        )
        
        # 3. Run ML Predictor
        ml_result = ml_predictor.predict(
            duration_weeks=extracted["extracted_duration_weeks"],
            conservative_tried=extracted["conservative_care_detected"],
            red_flags=extracted["red_flags_detected"],
            payer=payer,
            cpt=procedure_cpt
        )
        
        # 4. Hybrid Scoring (60% Rules + 40% ML)
        rule_conf = rule_result["confidence_score"] / 100.0
        ml_conf = ml_result["probability"]
        hybrid_score = round((0.6 * rule_conf + 0.4 * ml_conf) * 100, 1)
        
        # Final decision logic
        if hybrid_score >= 85:
            final_decision = "Strongly Recommended"
        elif hybrid_score >= 60:
            final_decision = "Review Suggested"
        else:
            final_decision = "Likely Rejected"
            
        return {
            "status": "success",
            "patient_id": patient_id,
            "extracted_features": extracted,
            "rule_engine": rule_result,
            "ml_prediction": ml_result,
            "hybrid_decision": {
                "final_recommendation": final_decision,
                "hybrid_confidence_score": hybrid_score,
                "ml_agrees_with_rules": (rule_result["decision"] == "Likely Approved") == (ml_conf > 0.6)
            }
        }
    except Exception as e:
        logger.error(f"Hybrid processing failed: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Processing failed"}