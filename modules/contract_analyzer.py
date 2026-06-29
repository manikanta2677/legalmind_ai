import re
from modules.clause_extractor import extract_clauses
from modules.risk_engine import calculate_risk


def is_legal_contract(text):
    lower = text.lower()

    strong_legal_phrases = [
        "this agreement is entered into",
        "this contract is entered into",
        "between",
        "hereinafter",
        "party of the first part",
        "party of the second part",
        "terms and conditions",
        "governing law",
        "termination clause",
        "confidentiality clause",
        "dispute resolution",
        "liability clause"
    ]

    score = 0

    for phrase in strong_legal_phrases:
        if phrase in lower:
            score += 1

    return score >= 3

def detect_contract_type(text):
    lower = text.lower()

    if not is_legal_contract(text):
        return "Not a Legal Contract"

    if "software" in lower or "source code" in lower or "application" in lower:
        return "Software Development Agreement"
    if "employment" in lower or "employee" in lower or "salary" in lower:
        return "Employment Contract"
    if "non-disclosure" in lower or "confidentiality" in lower:
        return "Non-Disclosure Agreement"
    if "service" in lower or "client" in lower:
        return "Service Agreement"
    if "lease" in lower or "rent" in lower:
        return "Lease Agreement"

    return "General Legal Contract"


def create_summary(text):
    sentences = re.split(r"[.!?]", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
    return ". ".join(sentences[:4]) + "." if sentences else "Summary not available."


def extract_entities(text):
    money = re.findall(r"(₹\s?\d+(?:,\d+)*|\$\s?\d+(?:,\d+)*|\d+\s?(?:rupees|dollars|INR|USD))", text, re.I)
    dates = re.findall(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d+\s?(?:days|months|years))", text, re.I)
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phones = re.findall(r"(\+?\d[\d\s-]{8,}\d)", text)

    parties = []
    match = re.search(r"between\s+(.+?)\s+and\s+(.+?)(?:\.|,|\n)", text, re.I | re.S)
    if match:
        parties = [match.group(1).strip(), match.group(2).strip()]

    return {
        "money": money,
        "dates": dates,
        "emails": emails,
        "phones": phones,
        "parties": parties
    }


def analyze_contract(text):
    print("NEW CONTRACT ANALYZER LOADED")
    if not is_legal_contract(text):
        return {
            "contract_type": "Not a Legal Contract",
            "summary": "Uploaded document does not appear to be a legal contract. Please upload a legal agreement/contract document.",
            "found_clauses": {},
            "missing_clauses": [],
            "risk_score": 0,
            "risk_level": "N/A",
            "risk_reasons": [],
            "entities": {
                "money": [],
                "dates": [],
                "emails": [],
                "phones": [],
                "parties": []
            }
        }

    found, missing = extract_clauses(text)
    risk_score, risk_level, risk_reasons = calculate_risk(missing)

    return {
        "contract_type": detect_contract_type(text),
        "summary": create_summary(text),
        "found_clauses": found,
        "missing_clauses": missing,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "entities": extract_entities(text)
    }