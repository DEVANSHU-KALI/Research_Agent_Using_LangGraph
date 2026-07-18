from retrievals.internet_retrieval import retrieve_internet
from retrievals.semantic_retrieval import retrieve_chunks
import asyncio

async def hybrid_retrieval(query: str) -> dict:
    semantic_results, internet_results = await asyncio.gather(retrieve_chunks(query), retrieve_internet(query))

    context = semantic_results["context"] + "\n\n" + internet_results["context"]

    return {
        'source':'hybrid',
        'context': context
    }