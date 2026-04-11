import pandas as pd
import random
import uuid
import os

# Ensure data directory exists
os.makedirs("app/data", exist_ok=True)

# Config
NUM_RECORDS = 150
PAYERS = ["Aetna", "BlueCross", "UnitedHealthcare", "Cigna", "Medicare"]
PROCEDURES = {
    "72148": ("MRI Lumbar Spine", "lower back pain", "lumbar"),
    "29881": ("Knee Arthroscopy", "knee instability", "knee"),
    "97110": ("Physical Therapy", "chronic musculoskeletal pain", "general"),
}
CONSERVATIVE_CARES = ["Physical Therapy", "NSAIDs", "Rest/Ice", "Chiropractic", "Steroid injections"]

def generate_clinical_notes(proc_name, symptom_area, duration_weeks, conservative_tried, red_flags):
    notes = []
    notes.append(f"Patient presents with chronic {symptom_area} for {duration_weeks} weeks.")
    if conservative_tried:
        tried = random.sample(CONSERVATIVE_CARES, k=random.randint(1, 3))
        notes.append(f"Failed conservative management: {', '.join(tried)}.")
    else:
        notes.append("No prior conservative management attempted.")
    if red_flags:
        notes.append("Red flags present: history of malignancy, unexplained weight loss.")
    else:
        notes.append("No red flags identified on initial assessment.")
    notes.append(f"Procedure {proc_name} medically necessary for diagnostic clarification and treatment planning.")
    return " ".join(notes)

data = []
for _ in range(NUM_RECORDS):
    auth_id = str(uuid.uuid4())[:8].upper()
    patient_id = f"P{random.randint(10000, 99999)}"
    age = random.randint(22, 78)
    gender = random.choice(["M", "F"])
    payer = random.choice(PAYERS)
    cpt = random.choice(list(PROCEDURES.keys()))
    proc_name, symptom_area, _ = PROCEDURES[cpt]
    duration = random.choice([2, 4, 8, 10, 12, 16, 20, 24, 36])
    conservative = random.choices([True, False], weights=[0.75, 0.25])[0]
    red_flags = random.choices([False, True], weights=[0.85, 0.15])[0]

    # Simulate insurance policy rules
    # Rule: >=12 weeks symptoms + failed conservative care + NO red flags
    duration_met = duration >= 12
    conservative_met = conservative
    red_flags_clear = not red_flags
    policy_met = duration_met and conservative_met and red_flags_clear

    # Outcome logic (realistic approval/denial rates)
    if policy_met:
        status = random.choices(["Approved", "Denied", "Pending"], weights=[0.88, 0.09, 0.03])[0]
    else:
        status = random.choices(["Denied", "Approved", "Pending"], weights=[0.80, 0.12, 0.08])[0]

    denial_reason = ""
    if status == "Denied":
        reasons = []
        if not duration_met: reasons.append("Duration of symptoms < 3 months")
        if not conservative_met: reasons.append("Failed conservative care not documented")
        if not red_flags_clear: reasons.append("Red flags require specialist referral first")
        denial_reason = "; ".join(reasons) if reasons else "Does not meet medical necessity criteria"

    notes = generate_clinical_notes(proc_name, symptom_area, duration, conservative, red_flags)

    data.append({
        "auth_id": auth_id, "patient_id": patient_id, "age": age, "gender": gender,
        "payer": payer, "procedure_cpt": cpt, "procedure_name": proc_name,
        "clinical_notes": notes, "symptom_duration_weeks": duration,
        "conservative_care_tried": conservative, "red_flags_present": red_flags,
        "policy_requirements_met": policy_met, "approval_status": status,
        "denial_reason": denial_reason
    })

df = pd.DataFrame(data)
df.to_csv("app/data/synthetic_prior_auth.csv", index=False)
print(f"✅ Generated {len(df)} synthetic prior auth records.")
print("\n📊 Sample rows:")
print(df[["procedure_name", "clinical_notes", "policy_requirements_met", "approval_status"]].head(3))