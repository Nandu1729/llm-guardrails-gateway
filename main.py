from dotenv import load_dotenv
load_dotenv()

from app.graph import app

DIVIDER = "─" * 55


def print_header():
    print("\n" + "═" * 55)
    print("   LLM Guardrails Gateway")
    print("   Powered by Groq + LangGraph")
    print("═" * 55)
    print('Type "exit" to quit.\n')


def run_query(user_input: str) -> dict:
    return app.invoke({
        "user_input": user_input,
        "sanitized_input": "",
        "llm_response": "",
        "final_response": "",
        "input_status": "",
        "output_status": "",
        "block_reason": "",
        "retry_count": 0,
        "policy_violations": [],
    })


def display_result(result: dict):
    print(f"\n{DIVIDER}")
    input_status = result.get("input_status", "")
    output_status = result.get("output_status", "")
    violations = result.get("policy_violations", [])
    retries = result.get("retry_count", 0)

    if input_status == "BLOCKED":
        print(f"  Input Guard   : BLOCKED")
        print(f"  Reason        : {result.get('block_reason', '')}")
    else:
        print(f"  Input Guard   : PASS")
        if retries > 0:
            print(f"  Output Retries: {retries}")
        verdict = "PASS" if output_status == "PASS" else "BLOCKED"
        print(f"  Output Guard  : {verdict}")

    if violations:
        print(f"  Violations    : {', '.join(violations)}")

    print(DIVIDER)
    print("\nResponse:\n")
    print(result.get("final_response", ""))
    print(f"\n{'═' * 55}\n")


def main():
    print_header()
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            if not user_input:
                continue
            result = run_query(user_input)
            display_result(result)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
