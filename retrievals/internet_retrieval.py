import os
from tavily import AsyncTavilyClient

client = AsyncTavilyClient(os.getenv("TAVILY_API_KEY"))

async def retrieve_internet(query: str) -> dict:

    tavily_response = await client.search(query)

    retrieved_results = []

    for result in tavily_response["results"]:
        retrieved_results.append(
            {
                'title': result["title"],
                "content": result["content"]
            }
        )
    
    context = "Internet Search Results:\n\n"
    context += "\n\n".join(
        f"**{result['title']}**\n{result['content']}"
        for result in retrieved_results
    )

    return {
        "source": "internet",
        "context": context,
    }