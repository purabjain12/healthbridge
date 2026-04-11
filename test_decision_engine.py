import pandas as pd
from app.core.extraction import process_clinical_notes
from app.core.decision_engine import PayerRuleEngine

df = pd.read_csv("app/data/synthetic_prior_auth.csv")
engine = PayerRuleEngine()

print("\n--- 📋 DECISION ENGINE VALIDATION (First 5 Records) ---")
correct_predictions = 0
total = 5

for idx, row in df.head(total).iterrows():
    # Step 1: Extract from notes
    extracted = process_clinical_notes(row['clinical_notes'])
    
    # Step 2: Run rule engine
    result = engine.evaluate(
        procedure_cpt=row['procedure_cpt'],
        extracted_duration=extracted['extracted_duration_weeks'],
        conservative_detected=extracted['conservative_care_detected'],
        red_flags_detected=extracted['red_flags_detected']
    )
    
    # Step 3: Compare with ground truth
    actual_approved = row['policy_requirements_met']
    predicted_approved = result['decision'] == "Likely Approved"
    match = actual_approved == predicted_approved
    
    if match: correct_predictions += 1
    
    print(f"\n🆔 {row['auth_id']} | {row['procedure_name']}")
    print(f"   Decision: {result['decision']} ({result['confidence_score']}%)")
    print(f"   Justification: {result['justification']}")
    print(f"   ✅ Matches Ground Truth: {match}")

print(f"\n🎯 Accuracy on sample: {correct_predictions}/{total} ({(correct_predictions/total)*100:.0f}%)")
