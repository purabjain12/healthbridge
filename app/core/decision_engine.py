class PayerRuleEngine:
    def __init__(self):
        # Simulated payer policy rules per CPT code
        # In production, this comes from a database or config file
        self.rules = {
            "72148": {  # MRI Lumbar Spine
                "duration_threshold_weeks": 12,
                "requires_conservative_care": True,
                "allows_red_flags": False
            },
            "29881": {  # Knee Arthroscopy
                "duration_threshold_weeks": 16,
                "requires_conservative_care": True,
                "allows_red_flags": True  # Trauma cases may bypass
            },
            "97110": {  # Physical Therapy
                "duration_threshold_weeks": 4,
                "requires_conservative_care": False,
                "allows_red_flags": True
            }
        }

    def evaluate(self, procedure_cpt, extracted_duration, conservative_detected, red_flags_detected):
        rule = self.rules.get(procedure_cpt, {
            "duration_threshold_weeks": 12,
            "requires_conservative_care": True,
            "allows_red_flags": False
        })

        checks = []
        passed = 0
        total_checks = 0

        # 1. Duration Check
        total_checks += 1
        if extracted_duration and extracted_duration >= rule["duration_threshold_weeks"]:
            passed += 1
            checks.append("✅ Symptom duration meets threshold")
        else:
            checks.append(f"❌ Duration too short (need ≥{rule['duration_threshold_weeks']}w, got {extracted_duration or 0}w)")

        # 2. Conservative Care Check
        total_checks += 1
        if rule["requires_conservative_care"]:
            if conservative_detected:
                passed += 1
                checks.append("✅ Conservative care documented")
            else:
                checks.append("❌ Missing conservative care documentation")
        else:
            passed += 1
            checks.append("ℹ️ Conservative care not required for this procedure")

        # 3. Red Flags Check
        total_checks += 1
        if red_flags_detected and not rule["allows_red_flags"]:
            checks.append("❌ Red flags present; requires specialist referral first")
        else:
            passed += 1
            checks.append("✅ No disqualifying red flags")

        # Calculate confidence & decision
        confidence = round((passed / total_checks) * 100, 1)
        if confidence == 100:
            decision = "Likely Approved"
        elif confidence >= 66:
            decision = "Review Required"
        else:
            decision = "Likely Denied"

        # Generate plain-language justification
        justification = self._build_justification(decision, checks)

        return {
            "decision": decision,
            "confidence_score": confidence,
            "checks_performed": checks,
            "justification": justification
        }

    def _build_justification(self, decision, checks):
        if decision == "Likely Approved":
            return "Clinical documentation satisfies payer medical necessity criteria. Auto-approval recommended."
        elif decision == "Review Required":
            issues = [c.replace("❌ ", "").replace("✅ ", "").replace("ℹ️ ", "") for c in checks if c.startswith("❌")]
            return f"Partial match. Missing: {', '.join(issues)}. Recommend adding supplemental documentation before submission."
        else:
            return f"Documentation insufficient for standard approval. Key gaps identified. Consider peer-to-peer review or appeal with additional clinical evidence."