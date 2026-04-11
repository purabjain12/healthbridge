import pandas as pd
from app.core.extraction import process_clinical_notes

# Load data
df = pd.read_csv("app/data/synthetic_prior_auth.csv")

results = []

# Run extraction on a sample of 5 records
for idx, row in df.head(5).iterrows():
    # Run NLP
    extracted = process_clinical_notes(row['clinical_notes'])
    
    # Calculate accuracy
    dur_acc = extracted['extracted_duration_weeks'] == row['symptom_duration_weeks']
    care_acc = extracted['conservative_care_detected'] == row['conservative_care_tried']
    flag_acc = extracted['red_flags_detected'] == row['red_flags_present']
    
    results.append({
        "auth_id": row['auth_id'],
        "Note Snippet": row['clinical_notes'][:50] + "...",
        "Duration Correct": dur_acc,
        "Care Correct": care_acc,
        "Red Flag Correct": flag_acc
    })

print("\n--- 🧪 EXTRACTION TEST RESULTS ---")
res_df = pd.DataFrame(results)
print(res_df.to_string(index=False))
print(f"\n✅ Total Correct: {res_df[['Duration Correct', 'Care Correct', 'Red Flag Correct']].sum().sum()} / {len(res_df)*3}")