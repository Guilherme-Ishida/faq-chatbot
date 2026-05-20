import re

_INJECTION_PATTERNS = [
    # Tentativas de sobrescrever instruções
    r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?",
    r"ignore\s+as\s+instru[çc][oõ]es\s+anteriores",
    r"esqueça\s+(as\s+)?instru[çc][oõ]es",
    r"forget\s+(all\s+)?(previous|prior|your)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+instructions?",

    # Tentativas de trocar de papel
    r"(you\s+are\s+now|agora\s+voc[eê]\s+[eé])\s+.{0,60}",
    r"act\s+as\s+(if\s+)?(you\s+are\s+)?a[n]?\s+",
    r"pretend\s+(you\s+are|to\s+be)\s+",
    r"finja\s+(que\s+voc[eê]\s+[eé]|ser)\s+",
    r"comporte[- ]se\s+como\s+",
    r"haja\s+como\s+",

    # Exfiltração do system prompt
    r"(repeat|repita|mostre?|show|reveal|print|display)\s+(me\s+)?(your|seu|o\s+seu)?\s*(system\s+)?prompt",
    r"(what\s+are|quais\s+s[ãa]o)\s+(your|suas)\s+instructions?",
    r"(tell|diga|liste?)\s+(me\s+)?(your|suas?)\s+(instructions?|regras|rules)",

    # Jailbreak clássicos
    r"\bDAN\b",
    r"do\s+anything\s+now",
    r"jailbreak",
    r"modo?\s+deus",
    r"god\s+mode",
    r"developer\s+mode",
    r"modo?\s+desenvolvedor",

    # Injeção via delimitadores
    r"```\s*system",
    r"<\s*system\s*>",
    r"\[INST\]",
    r"<<SYS>>",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def has_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in _COMPILED)
