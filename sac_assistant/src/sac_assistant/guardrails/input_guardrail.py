import re

CPF_PATTERN = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")
CARD_PATTERN = re.compile(r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}")
INJECTION_PATTERNS = [
    re.compile(r"ignore (your |all )?(previous |prior )?instructions", re.IGNORECASE),
    re.compile(r"ignore suas instru", re.IGNORECASE),
    re.compile(r"you are now", re.IGNORECASE),
    re.compile(r"aja como se", re.IGNORECASE),
    re.compile(r"system prompt", re.IGNORECASE),
    re.compile(r"revele (seu|o) prompt", re.IGNORECASE),
]


def check_input(question: str) -> tuple[bool, str]:
    if CPF_PATTERN.search(question) or CARD_PATTERN.search(question):
        return False, "pii_detected"

    for pattern in INJECTION_PATTERNS:
        if pattern.search(question):
            return False, "prompt_injection_detected"

    return True, ""