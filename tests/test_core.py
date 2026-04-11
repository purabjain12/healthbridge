import pytest
from app.core.extraction import process_clinical_notes
from app.core.decision_engine import PayerRuleEngine

def test_extraction_duration():
    notes = "Chronic knee pain for 6 months."
    result = process_clinical_notes(notes)
    assert result["extracted_duration_weeks"] is not None
    assert 25 <= result["extracted_duration_weeks"] <= 27  # ~6 months

def test_extraction_conservative_care():
    notes = "Failed PT and NSAIDs after 8 weeks."
    result = process_clinical_notes(notes)
    assert result["conservative_care_detected"] is True

def test_extraction_red_flags():
    notes = "No red flags identified."
    assert process_clinical_notes(notes)["red_flags_detected"] is False

def test_rule_engine_approved():
    engine = PayerRuleEngine()
    res = engine.evaluate("72148", 16, True, False)
    assert res["decision"] == "Likely Approved"
    assert res["confidence_score"] == 100.0

def test_rule_engine_denied():
    engine = PayerRuleEngine()
    res = engine.evaluate("72148", 8, False, False)
    assert "Denied" in res["decision"]
    assert res["confidence_score"] <= 66.0