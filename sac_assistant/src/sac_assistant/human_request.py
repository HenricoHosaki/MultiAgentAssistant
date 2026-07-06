import re

_HUMAN_REQUEST_PATTERNS = [
    re.compile(r"\b(talk|speak) (to|with) (an?\s*human|someone)\b", re.IGNORECASE),
    re.compile(r"\bhuman agent\b", re.IGNORECASE),
    re.compile(r"\breal person\b", re.IGNORECASE),
    re.compile(r"\bcustomer service (agent|rep)\b", re.IGNORECASE),
    re.compile(r"falar com (um )?(atendente|humano|alguém|alguem)", re.IGNORECASE),
    re.compile(r"atendimento humano", re.IGNORECASE),
    re.compile(r"quero (um )?atendente", re.IGNORECASE),
    re.compile(r"pessoa (de verdade|real)", re.IGNORECASE),
]


def wants_human(text: str) -> bool:
    return any(pattern.search(text) for pattern in _HUMAN_REQUEST_PATTERNS)
