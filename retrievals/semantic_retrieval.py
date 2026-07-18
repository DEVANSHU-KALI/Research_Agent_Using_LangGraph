from one_time.qdrant_client import qdrant_client, COLLECTION_NAME
from one_time.embedding_model import embedding_model

async def retrieve_chunks(query: str) -> dict:

    query_embedding =  embedding_model.embed_query(query)

    result = await qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit = 3
    )
    
    retrieve_chunks = []

    for point in result.points:
        retrieve_chunks.append(
            {
            'text': point.payload['text']
            }
        )

    context = "Local Knowledge Base:\n\n"
    context += "\n\n".join(
        chunk['text'] for chunk in retrieve_chunks
    )

    return {
        "source":"semantic",
        "context":context
    }