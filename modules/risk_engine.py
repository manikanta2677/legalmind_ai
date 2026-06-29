RISK_WEIGHTS = {
    "Payment Clause": 12,
    "Termination Clause": 15,
    "Confidentiality Clause": 10,
    "Liability Clause": 18,
    "Dispute Resolution Clause": 14,
    "Governing Law Clause": 10,
    "Intellectual Property Clause": 12,
    "Renewal Clause": 6,
    "Force Majeure Clause": 5,
    "Indemnity Clause": 12,
    "Data Protection Clause": 10,
    "Non-Compete Clause": 6
}


RISK_REASONS = {
    "Payment Clause": "Payment terms are unclear, which may cause financial disputes.",
    "Termination Clause": "No clear exit condition is defined.",
    "Confidentiality Clause": "Sensitive information may not be protected.",
    "Liability Clause": "Responsibility for damages is not clearly defined.",
    "Dispute Resolution Clause": "No method is defined for solving disputes.",
    "Governing Law Clause": "Applicable law is not mentioned.",
    "Intellectual Property Clause": "Ownership of work/products is unclear.",
    "Renewal Clause": "Renewal conditions are not defined.",
    "Force Majeure Clause": "Unexpected events are not handled.",
    "Indemnity Clause": "Protection from third-party claims is missing.",
    "Data Protection Clause": "Data/privacy responsibilities are unclear.",
    "Non-Compete Clause": "Competition restrictions are not defined."
}


def calculate_risk(missing_clauses):
    score = sum(RISK_WEIGHTS.get(c, 5) for c in missing_clauses)
    score = min(score, 100)

    if score <= 30:
        level = "Low Risk"
    elif score <= 60:
        level = "Medium Risk"
    else:
        level = "High Risk"

    reasons = [RISK_REASONS.get(c, "Important clause missing.") for c in missing_clauses]

    return score, level, reasons