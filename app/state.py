from typing import TypedDict, List


class GatewayState(TypedDict):
    user_input: str
    sanitized_input: str
    llm_response: str
    final_response: str
    input_status: str       # PASS or BLOCKED
    output_status: str      # PASS or FAIL
    block_reason: str
    retry_count: int
    policy_violations: List[str]
