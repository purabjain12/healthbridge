import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Load synthetic data
df = pd.read_csv("app/data/synthetic_prior_auth.csv")

# Feature Engineering
df['duration_met'] = (df['symptom_duration_weeks'] >= 12).astype(int)
df['conservative_tried'] = df['conservative_care_tried'].astype(int)
df['no_red_flags'] = (~df['red_flags_present']).astype(int)

# One-hot encode categorical features (fixed for baseline)
df = pd.get_dummies(df, columns=['payer', 'procedure_cpt'], drop_first=True)

# Target: 1 = Approved, 0 = Denied/Pending
df['target'] = (df['approval_status'] == 'Approved').astype(int)

# Define feature columns explicitly to avoid train/predict mismatch later
base_features = ['duration_met', 'conservative_tried', 'no_red_flags']
cat_features = [col for col in df.columns if col.startswith('payer_') or col.startswith('procedure_cpt_')]
feature_cols = base_features + cat_features

X = df[feature_cols].fillna(0)
y = df['target']

# Train/Test Split (stratify to keep class balance)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train Model
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
print("\n--- 🤖 MODEL PERFORMANCE ---")
print(f"Accuracy: {accuracy_score(y_test, preds):.2f}")
print("\nClassification Report:")
print(classification_report(y_test, preds, target_names=['Denied/Pending', 'Approved']))

# Save Model
os.makedirs("app/models", exist_ok=True)
joblib.dump(model, "app/models/approval_predictor.pkl")
print("\n✅ Model saved to app/models/approval_predictor.pkl")
print("💡 Feature importance will be used later for explainability.")