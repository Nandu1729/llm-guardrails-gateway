import os
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)


def llm_call(state):
    response = llm.invoke(state["sanitized_input"])
    return {"llm_response": response.content.strip()}
