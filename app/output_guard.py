import re
import json
import os
from langchain_groq import ChatGroq
from app.policy import get_policy

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

TOXIC_PATTERNS = [
    r"\b(kill|murder|genocide|terrorist|bomb|weapon)\b",
    r"\b(explicit|graphic)\s+(violence|sexual content)\b",
]


def output_guard(state):
    policy = get_policy()
    response = state["llm_response"]
    og = policy.get("output_guardrails", {})
    violations = []

    if og.get("require_json", False):
        try:
            json.loads(response)
        except json.JSONDecodeError:
            violations.append("invalid_json_schema")

    if og.get("check_toxicity", True):
        for pattern in TOXIC_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                violations.append("toxic_content")
                break

    if og.get("check_topic_adherence", True):
        never_discuss = policy.get("rules", {}).get("never_discuss", [])
        if never_discuss:
            topics = ", ".join(never_discuss)
            check_prompt = f"""Does the following response discuss any of these forbidden topics: {topics}?

Response: {response}

Reply with ONLY one word — YES or NO."""
            check = llm.invoke(check_prompt)
            if "YES" in check.content.strip().upper():
                violations.append("off_topic_policy_violation")

    max_retries = og.get("max_retries", 3)
    retry_count = state.get("retry_count", 0)
    existing_violations = state.get("policy_violations", [])

    if violations:
        return {
            "output_status": "FAIL",
            "retry_count": retry_count + 1,
            "policy_violations": existing_violations + violations,
            "final_response": policy.get("fallback_message", "Unable to generate a safe response.") if retry_count + 1 >= max_retries else "",
        }

    return {
        "output_status": "PASS",
        "final_response": response,
        "policy_violations": existing_violations,
    }
