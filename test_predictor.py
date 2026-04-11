import pandas as pd
import joblib

# 1. Load model
model = joblib.load("app/models/approval_predictor.pkl")

# 2. Load RAW data
df = pd.read_csv("app/data/synthetic_prior_auth.csv")

# 3. REPLICATE TRAINING PREPROCESSING
# We must create the exact features the model expects
df_test = df.copy()
df_test['duration_met'] = (df_test['symptom_duration_weeks'] >= 12).astype(int)
df_test['conservative_tried'] = df_test['conservative_care_tried'].astype(int)
df_test['no_red_flags'] = (~df_test['red_flags_present']).astype(int)

# One-hot encode (mimic training logic)
df_test = pd.get_dummies(df_test, columns=['payer', 'procedure_cpt'], drop_first=True)

# 4. ALIGN COLUMNS
# Ensure the dataframe has all columns the model was trained on (fill missing with 0)
for col in model.feature_names_in_:
    if col not in df_test.columns:
        df_test[col] = 0

# Select columns in exact order the model expects
X_test_row = df_test[model.feature_names_in_].iloc[[0]]

# 5. PREDICT
pred = model.predict(X_test_row)[0]
prob = model.predict_proba(X_test_row)[0][1]

print(f"\n🔮 ML PREDICTION:")
print(f"Patient: {df.iloc[0]['patient_id']} | Actual: {df.iloc[0]['approval_status']} | Predicted: {'Approved' if pred else 'Denied'}")
print(f"ML Confidence: {prob*100:.1f}%")