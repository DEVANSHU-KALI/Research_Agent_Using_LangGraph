from langchain_openai import ChatOpenAI
import os

llm_model = ChatOpenAI(
model="llama-3.1-8b-instant",
base_url="https://api.groq.com/openai/v1",
api_key=os.getenv("GROQ_API_KEY")
)

async def generate_answer(query: str, retrieval_results: list[dict], feedback: str = "") -> dict:
    # 1. Merge the list of contexts from all executed retrieval nodes
    contexts = [res["context"] for res in retrieval_results]
    merged_context = "\n\n".join(contexts)

    # 2. Append feedback instructions if we are regenerating
    feedback_instruction = ""
    if feedback:
        feedback_instruction = f"\n\nCRITICAL FEEDBACK ON PREVIOUS RESPONSE:\nThe reviewer rejected your last response with this critique:\n\"{feedback}\"\nRead this feedback carefully and completely resolve the issue in your new answer."

    # 3. Combined Prompt: Factual Generation + Formatting
    prompt = f"""
    You are the Generator Node of a Hybrid GraphRAG system.

    Your responsibility is to generate a single, well-structured, professional answer
    using ONLY the retrieved context provided below.{feedback_instruction}

    Instructions:
    1. Read the entire retrieved context and integrate information naturally into ONE coherent answer.
    2. Organize the response into a professional and easy-to-read format. Use bullet points and emojis to make it look visually appealing.
    3. Do not mention "Local Knowledge Base", "Internet Search Results", or internal mechanics.
    4. If the context does not contain enough information, clearly state that the available info is insufficient.

    Retrieved Context:
    {merged_context}

    User Question:
    {query}

    Answer:
    """
    response = await llm_model.ainvoke([prompt])

    return {
        'answer': response.content,
    }