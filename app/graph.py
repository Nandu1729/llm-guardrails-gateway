from langgraph.graph import StateGraph, END
from app.state import GatewayState
from app.input_guard import input_guard
from app.llm_call import llm_call
from app.output_guard import output_guard
from app.policy import get_policy

MAX_RETRIES = 3


def blocked_node(state):
    if not state.get("final_response"):
        policy = get_policy()
        return {"final_response": policy.get("fallback_message", "Request blocked by safety policy.")}
    return {}


def route_after_input(state):
    if state.get("input_status") == "BLOCKED":
        return "blocked"
    return "llm_call"


def route_after_output(state):
    policy = get_policy()
    max_retries = policy.get("output_guardrails", {}).get("max_retries", MAX_RETRIES)

    if state.get("output_status") == "PASS":
        return END

    if state.get("retry_count", 0) >= max_retries:
        return "blocked"

    return "llm_call"


workflow = StateGraph(GatewayState)

workflow.add_node("input_guard", input_guard)
workflow.add_node("llm_call", llm_call)
workflow.add_node("output_guard", output_guard)
workflow.add_node("blocked", blocked_node)

workflow.set_entry_point("input_guard")

workflow.add_conditional_edges(
    "input_guard",
    route_after_input,
    {"blocked": "blocked", "llm_call": "llm_call"},
)

workflow.add_edge("llm_call", "output_guard")

workflow.add_conditional_edges(
    "output_guard",
    route_after_output,
    {END: END, "blocked": "blocked", "llm_call": "llm_call"},
)

workflow.add_edge("blocked", END)

app = workflow.compile()
