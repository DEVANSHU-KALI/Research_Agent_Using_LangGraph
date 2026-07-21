from pydantic import BaseModel, Field
from typing import Literal, Optional
from router.query_router import client

class ReviewSchema(BaseModel):
    status: Literal["pass", "fail"]
    feedback: Optional[str] = Field(
        default="",
        description="Detailed feedback if status is 'fail'. Specify what is missing or incorrect. If status is 'pass', return an empty string ''."
    )

async def review_answer(query: str, answer: str, retrieval_results: list[dict]) -> dict:
    contexts = [res["context"] for res in retrieval_results]
    merged_context = "\n\n".join(contexts)

    prompt = f"""
    You are the Reviewer Node of a Hybrid GraphRAG system.

    Your responsibility is to review the generated answer against the user's question and the retrieved context.
    Perform the following checks:
    1. Relevance: Does the answer directly address the user's question?
    2. Factuality: Is the answer strictly supported by the retrieved context? Does it contain hallucinations?

    Classify the status as 'pass' if the answer is accurate and fully addresses the question.
    Classify the status as 'fail' if the answer is missing critical details, contains inaccuracies, or does not directly answer the question.
    If 'fail', provide detailed feedback on what needs to be corrected or added.

    Retrieved Context:
    {merged_context}

    Generated Answer:
    {answer}

    User Question:
    {query}

    Return a JSON object with keys 'status' and 'feedback'.
    """
    structured_llm = client.with_structured_output(ReviewSchema, method="json_mode")
    response = await structured_llm.ainvoke(prompt)

    # Print the evaluation status directly to the terminal logs
    print(f"\n--- [REVIEWER NODE] Evaluation Status: {response.status.upper()} ---")
    if response.status == "fail":
        print(f"Feedback: {response.feedback or ''}\n")

    return {
        'status': response.status,
        'feedback': (response.feedback or "") if response.status == "fail" else ""
    }