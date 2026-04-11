import joblib
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class MLApprovalPredictor:
    def __init__(self, model_path="app/models/approval_predictor.pkl"):
        try:
            self.model = joblib.load(model_path)
            self.expected_features = list(self.model.feature_names_in_)
            logger.info("✅ ML Predictor loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load ML model: {e}")
            self.model = None

    def predict(self, duration_weeks: float, conservative_tried: bool, red_flags: bool, payer: str, cpt: str) -> dict:
        if self.model is None:
            return {"probability": 0.5, "error": "Model not loaded"}

        try:
            # Replicate exact training preprocessing
            features = {
                "duration_met": 1 if duration_weeks and duration_weeks >= 12 else 0,
                "conservative_tried": 1 if conservative_tried else 0,
                "no_red_flags": 1 if not red_flags else 0,
                "payer_Aetna": 1 if payer == "Aetna" else 0,
                "payer_BlueCross": 1 if payer == "BlueCross" else 0,
                "payer_Cigna": 1 if payer == "Cigna" else 0,
                "payer_Medicare": 1 if payer == "Medicare" else 0,
                "payer_UnitedHealthcare": 1 if payer == "UnitedHealthcare" else 0,
                "procedure_cpt_72148": 1 if cpt == "72148" else 0,
                "procedure_cpt_29881": 1 if cpt == "29881" else 0,
                "procedure_cpt_97110": 1 if cpt == "97110" else 0,
            }

            # Align with model's exact column order
            X = pd.DataFrame([features]).reindex(columns=self.expected_features, fill_value=0)
            prob = self.model.predict_proba(X)[0][1]
            return {"probability": round(float(prob), 3), "error": None}
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return {"probability": 0.5, "error": str(e)}

# Singleton instance
ml_predictor = MLApprovalPredictor()