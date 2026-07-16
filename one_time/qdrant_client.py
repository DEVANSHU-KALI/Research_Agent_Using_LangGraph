from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

qdrant_client = AsyncQdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "research_agent"

async def initialize_qdrant() -> None:
    try:
        collections = await qdrant_client.get_collections()

        collection_names = [collection.name for collection in collections.collections]

        if COLLECTION_NAME not in collection_names:
            await qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
            print('collection created!!')
        else:
            print('collection already exists')
    except Exception as error:
        print(f"failed to initialize collection {error}")

        raise

import asyncio

if __name__ == "__main__":
    asyncio.run(initialize_qdrant())