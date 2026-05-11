# LLM Guardrails Gateway

A middleware layer that sits between the user and any LLM, enforcing safety, compliance, and output structure rules — powered by **Groq + LangGraph**.

---

## How It Works

```
User Input → Input Guard → LLM (Groq) → Output Guard → Response
                 ↓                            ↓
             BLOCKED                     FAIL → Retry (max 3x)
                                              → Safe Fallback
```

---

## Features

### Input Guardrails
- **Prompt Injection** — blocks attempts to hijack AI instructions
- **Jailbreak Detection** — catches DAN-style and bypass attempts
- **PII Detection** — blocks credit cards, SSNs, phone numbers
- **Context-aware card detection** — catches partial numbers with card-related keywords
- **Adult Content Filtering** — blocks explicit/NSFW requests

### Output Guardrails
- **Toxicity Check** — scans LLM response for harmful content
- **Topic Adherence** — ensures response doesn't discuss forbidden topics
- **JSON Schema Validation** — optional, enforces structured output
- **Auto-retry** — retries up to 3x on failure before safe fallback

### Policy Engine
Configure everything via `policy.yaml` — no code changes needed:
```yaml
rules:
  never_discuss:
    - competitors

input_guardrails:
  block_prompt_injection: true
  block_jailbreak: true
  block_pii: true
  block_adult_content: true

output_guardrails:
  check_toxicity: true
  check_topic_adherence: true
  max_retries: 3
```

---

## Project Structure

```
llm-guardrails-gateway/
├── main.py                  # Entry point
├── policy.yaml              # Configurable rules
├── requirements.txt
├── .env.example
└── app/
    ├── state.py             # GatewayState
    ├── graph.py             # LangGraph workflow
    ├── input_guard.py       # Input guardrails
    ├── llm_call.py          # Groq LLM call
    ├── output_guard.py      # Output guardrails
    └── policy.py            # YAML policy loader
```

---

## Setup

```bash
git clone https://github.com/Nandu1729/llm-guardrails-gateway
cd llm-guardrails-gateway
pip3 install -r requirements.txt
cp .env.example .env        # Add your GROQ_API_KEY
python3 main.py
```

---

## Example

```
You: 923451. This is my card, save it.
──────────────────────────────────────
  Input Guard   : BLOCKED
  Reason        : pii_credit_card, pii_sensitive_number
──────────────────────────────────────
Response: I'm unable to process this request due to safety or policy constraints.

You: What is Python programming?
──────────────────────────────────────
  Input Guard   : PASS
  Output Guard  : PASS
──────────────────────────────────────
Response: Python is a high-level, interpreted programming language...
```

---

## Tech Stack

- [Groq](https://groq.com/) — LLM inference (llama-3.1-8b-instant)
- [LangGraph](https://github.com/langchain-ai/langgraph) — workflow graph
- [LangChain](https://github.com/langchain-ai/langchain) — LLM integration
- [PyYAML](https://pyyaml.org/) — policy engine

---

## Inspired By

Built using the same pattern as the [Self-Healing RAG Pipeline](https://github.com/Nandu1729/self-healing-rag).
