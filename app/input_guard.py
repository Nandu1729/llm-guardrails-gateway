import re
from app.policy import get_policy

INJECTION_PATTERNS = [
    r"ignore (all |previous |prior |above |your )?(instructions|rules|guidelines|prompt)",
    r"you are now",
    r"pretend (you are|to be)",
    r"act as (a|an|if)",
    r"disregard (all |your |previous )?instructions",
    r"override (your |the )?instructions",
    r"forget (everything|all|your instructions)",
    r"new (persona|role|instructions|rules)",
    r"\bsystem prompt\b",
    r"\bdeveloper mode\b",
]

JAILBREAK_PATTERNS = [
    r"\bDAN\b",
    r"do anything now",
    r"\bjailbreak\b",
    r"no restrictions",
    r"without (any |ethical )?constraints",
    r"as an? (unfiltered|unrestricted|uncensored)",
    r"evil (mode|ai|bot)",
    r"bypass (safety|filter|restriction)",
]

ADULT_PATTERNS = [
    r"\bporn(ography|o|hub)?\b",
    r"\bxxx\b",
    r"\bnsfw\b",
    r"\bsex (sites?|videos?|content)\b",
    r"\bnude(s)?\b",
    r"\bexplicit (content|sites?|videos?)\b",
    r"\badult (sites?|content|videos?)\b",
    r"\bstrip(per|club)?\b",
    r"\berotic\b",
]

PII_PATTERNS = {
    "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
}

# Catches partial card numbers mentioned with card-related keywords
CARD_INTENT_PATTERN = re.compile(
    r"(card|credit|debit|cvv|pin|account).{0,30}\d{4,}|\d{4,}.{0,30}(card|credit|debit|cvv|pin|account)",
    re.IGNORECASE,
)

SAVE_INTENT_PATTERN = re.compile(
    r"(save|store|remember|keep).{0,30}\d{4,}|\d{4,}.{0,30}(save|store|remember|keep)",
    re.IGNORECASE,
)


def input_guard(state):
    policy = get_policy()
    original = state["user_input"]
    text_lower = original.lower()
    violations = []

    ig = policy.get("input_guardrails", {})

    if ig.get("block_adult_content", True):
        for pattern in ADULT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append("adult_content")
                break

    if ig.get("block_prompt_injection", True):
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                violations.append("prompt_injection")
                break

    if ig.get("block_jailbreak", True):
        for pattern in JAILBREAK_PATTERNS:
            if re.search(pattern, original, re.IGNORECASE):
                violations.append("jailbreak_attempt")
                break

    if ig.get("block_pii", True):
        for pii_type, pattern in PII_PATTERNS.items():
            if re.search(pattern, original):
                violations.append(f"pii_{pii_type}")
        if CARD_INTENT_PATTERN.search(original):
            violations.append("pii_credit_card")
        if SAVE_INTENT_PATTERN.search(original):
            violations.append("pii_sensitive_number")

    never_discuss = policy.get("rules", {}).get("never_discuss", [])
    for topic in never_discuss:
        if topic.lower() in text_lower:
            violations.append(f"policy_violation:{topic}")

    if violations:
        fallback_msg = policy.get("fallback_message", "This request cannot be processed.")
        return {
            "input_status": "BLOCKED",
            "block_reason": ", ".join(violations),
            "final_response": fallback_msg,
            "sanitized_input": original,
            "policy_violations": violations,
        }

    return {
        "input_status": "PASS",
        "sanitized_input": original,
        "block_reason": "",
        "policy_violations": [],
    }
