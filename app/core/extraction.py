import re
import pandas as pd

# --- Configuration ---
# Keywords that indicate conservative care was attempted
CONSERVATIVE_KEYWORDS = ["physical therapy", "PT", "NSAIDs", "ibuprofen", "rest", "chiropractic", "injections"]
RED_FLAG_KEYWORDS = ["red flags", "malignancy", "cancer", "weight loss", "trauma", "infection"]

def extract_duration_weeks(text):
    """Extracts duration from text like 'pain for 6 months' -> 26"""
    text = text.lower()
    
    # Pattern: number + (month|weeks|wk|mo)
    match = re.search(r'(\d+)\s*(month|mo|weeks|wk|week)', text)
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        if 'mo' in unit or 'month' in unit:
            return val * 4.3  # Approximate weeks in a month
        return val
    return None

def check_conservative_care(text):
    """Returns True if conservative care is mentioned as failed/tried."""
    text_lower = text.lower()
    # Simple keyword match + check for context words like 'failed', 'unresponsive', 'tried'
    context_words = ["failed", "tried", "unresponsive", "attempted", "history of"]
    
    found_treatment = any(kw.lower() in text_lower for kw in CONSERVATIVE_KEYWORDS)
    found_context = any(ctx in text_lower for ctx in context_words)
    
    return found_treatment and found_context

def check_red_flags(text):
    """Returns True if red flags are mentioned."""
    text_lower = text.lower()
    
    # 1. Check for explicit negations FIRST
    negations = ["no red flags", "without red flags", "absence of red flags", "negative for red flags"]
    if any(neg in text_lower for neg in negations):
        return False
        
    # 2. Fall back to keyword match
    return any(kw.lower() in text_lower for kw in RED_FLAG_KEYWORDS)

def process_clinical_notes(notes_text):
    """Main wrapper to process a single note string."""
    return {
        "extracted_duration_weeks": extract_duration_weeks(notes_text),
        "conservative_care_detected": check_conservative_care(notes_text),
        "red_flags_detected": check_red_flags(notes_text)
    }