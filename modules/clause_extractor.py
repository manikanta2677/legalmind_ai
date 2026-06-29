import re

CLAUSE_PATTERNS = {
    "Payment Clause": [
        "payment", "invoice", "fees", "amount",
        "charges", "compensation", "advance payment"
    ],

    "Termination Clause": [
        "terminate", "termination", "notice period",
        "termination notice", "cancel agreement"
    ],

    "Confidentiality Clause": [
        "confidential", "confidentiality",
        "non disclosure", "non-disclosure",
        "proprietary information"
    ],

    "Liability Clause": [
        "liability",
        "liable for damages",
        "limitation of liability",
        "consequential damages"
    ],

    "Dispute Resolution Clause": [
        "dispute resolution",
        "arbitration",
        "jurisdiction",
        "court of law",
        "mediation"
    ],

    "Governing Law Clause": [
        "governing law",
        "laws of",
        "applicable law"
    ],

    "Intellectual Property Clause": [
        "intellectual property",
        "copyright",
        "trademark",
        "ownership of source code",
        "ownership rights"
    ],

    "Renewal Clause": [
        "contract renewal",
        "renewal period",
        "automatic renewal",
        "renewal term"
    ],

    "Force Majeure Clause": [
        "force majeure",
        "act of god",
        "natural disaster",
        "pandemic"
    ],

    "Indemnity Clause": [
        "indemnify",
        "indemnification",
        "hold harmless"
    ],

    "Data Protection Clause": [
        "data protection",
        "personal data",
        "privacy policy",
        "gdpr"
    ],

    "Non-Compete Clause": [
        "non compete",
        "non-compete",
        "competition restriction"
    ]
}


def split_paragraphs(text):
    paragraphs = re.split(r"\n\s*\n", text)

    return [
        p.strip()
        for p in paragraphs
        if len(p.strip()) > 30
    ]


def exact_match(keyword, text):
    pattern = r"\b" + re.escape(keyword.lower()) + r"\b"
    return re.search(pattern, text.lower()) is not None


def extract_clauses(text):

    paragraphs = split_paragraphs(text)

    found = {}
    missing = []

    for clause, keywords in CLAUSE_PATTERNS.items():

        best_para = None
        matches = []

        for para in paragraphs:

            para_matches = []

            for keyword in keywords:

                if exact_match(keyword, para):
                    para_matches.append(keyword)

            if len(para_matches) > len(matches):
                matches = para_matches
                best_para = para

        if best_para:

            confidence = min(
                100,
                60 + len(matches) * 10
            )

            found[clause] = {
                "text": best_para,
                "keywords": matches,
                "confidence": confidence
            }

        else:
            missing.append(clause)

    return found, missing