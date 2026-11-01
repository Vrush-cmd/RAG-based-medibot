from __future__ import annotations

import re

EMERGENCY_PATTERNS = {
    "chest pain": "Call 999 now (UK), or your local emergency number.",
    "trouble breathing": "Call 999 now (UK), or your local emergency number.",
    "difficulty breathing": "Call 999 now (UK), or your local emergency number.",
    "stroke": "Call 999 now (UK), or your local emergency number.",
    "face drooping": "Call 999 now (UK), or your local emergency number.",
    "severe bleeding": "Call 999 now (UK), or your local emergency number.",
    "overdose": "Call 999 now (UK). Do not wait for symptoms.",
    "poisoning": "Call 999 now (UK), or contact NHS 111 for urgent advice.",
    "severe allergic": "Call 999 now (UK), or your local emergency number.",
    "anaphylaxis": "Call 999 now (UK), or your local emergency number.",
    "suicid": "Call 999 now (UK) if you may act soon. You can also call Samaritans on 116 123.",
    "self-harm": "Call 999 now (UK) if you may act soon. You can also call Samaritans on 116 123.",
}

OUT_OF_SCOPE = (
    r"\bdo i have\b", r"\bam i suffering from\b", r"\bdiagnos(?:e|is|ing)\b",
    r"\bdose\b", r"\bdosage\b", r"\bhow much .* take\b", r"\bdrug interaction\b",
    r"\bmedication interaction\b", r"\bfor my child\b", r"\bwhile pregnant\b",
    r"\bpregnancy dosing\b",
)


def safety_check(question: str) -> tuple[str, str | None]:
    """Return (kind, notice), before retrieval or generation."""
    normalized = re.sub(r"\s+", " ", question.lower()).strip()
    for pattern, advice in EMERGENCY_PATTERNS.items():
        if pattern in normalized:
            return "emergency", advice
    if any(re.search(pattern, normalized) for pattern in OUT_OF_SCOPE):
        return "out_of_scope", (
            "I can share general information from my sources, but I can’t diagnose, "
            "recommend a personal dose, or check a personal treatment plan. Please "
            "speak with a clinician, pharmacist, or the product label."
        )
    return "ok", None

