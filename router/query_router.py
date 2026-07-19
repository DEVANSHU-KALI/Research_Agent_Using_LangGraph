from langchain_openai import ChatOpenAI
import os
from pydantic import BaseModel
from typing import Literal

client = ChatOpenAI(
    model="llama-3.1-8b-instant",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
    )

class RouterSchema(BaseModel):
    decision: Literal["semantic", "internet", "hybrid"]

async def supervisor(query: str) -> dict:
    prompt = f"""
    You are the Supervisor Node of a Hybrid GraphRAG system.

Your responsibility is to determine the MINIMUM retrieval strategy
required to answer the user's question.

Available retrieval strategies:

1. semantic
- Use when the question can be answered using the organization's
  internal knowledge base.
- Examples:
  - Company policies
  - Employee information
  - Internal project documentation
  - Uploaded documents
  - Private organizational knowledge

2. internet
- Use when the question requires public or recent information.
- Examples:
  - Current news
  - Weather
  - Sports
  - Public company information
  - Recent events

3. hybrid
- Use ONLY when BOTH the internal knowledge base AND internet
  information are genuinely required to answer the question.
- Examples:
  - Compare our employee salaries with industry salaries.
  - Compare our AI model with the latest public models.
  - Compare our internal policies with government regulations.

Rules:

- Always choose the MINIMUM retrieval strategy needed.
- Do not choose hybrid unless both sources are necessary.
- Return a JSON object with a single key 'decision' containing one of: 'semantic', 'internet', 'hybrid'.

Examples:

    Question:
    "What is our leave policy?"
    Output:
    {{"decision": "semantic"}}

    Question:
    "What is today's weather in usa?"
    Output:
    {{"decision": "internet"}}

    Question:
    "Compare our AI Engineer salary with the current market salary."
    Output:
    {{"decision": "hybrid"}}

Possible outputs:

{{"decision": "semantic"}}

{{"decision": "internet"}}

{{"decision": "hybrid"}}

User Question:
{query}
"""
    # Force JSON mode for compatibility with llama-3.1-8b-instant
    structured_llm = client.with_structured_output(RouterSchema, method="json_mode")
    response = await structured_llm.ainvoke(prompt)

    return {
        'decision': response.decision,
        'query': query,
    }