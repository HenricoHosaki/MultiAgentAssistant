import re

_ABOUT_PATTERNS = [
    re.compile(r"\bwhat (can|do) you do\b", re.IGNORECASE),
    re.compile(r"\bwho are you\b", re.IGNORECASE),
    re.compile(r"\bhow can you help( me)?\b", re.IGNORECASE),
    re.compile(r"\babout you(rself)?\b", re.IGNORECASE),
    re.compile(r"o que (você|voce|vc) (consegue|pode|sabe) fazer", re.IGNORECASE),
    re.compile(r"o que (você|voce|vc) faz\b", re.IGNORECASE),
    re.compile(r"quem (é|e) (você|voce|vc)", re.IGNORECASE),
    re.compile(r"como (você|voce|vc) (pode|consegue) me ajudar", re.IGNORECASE),
    re.compile(r"sobre (você|voce|vc)( mesma)?\b", re.IGNORECASE),
]


def wants_about_info(text: str) -> bool:
    return any(pattern.search(text) for pattern in _ABOUT_PATTERNS)
