# Explanations of One-Time Scripts

This file contains the detailed explanation for all the utility scripts located in the `one_time` folder. These scripts are responsible for setting up the vector database, loading the local embedding model, chunking raw document texts semantically, and ingesting them to create a RAG knowledge base.

---

## 1. embedding_model.py

### What this script is
This script initializes our text embedding model. It loads a pre-trained model from Hugging Face using the LangChain library to convert textual strings into dense numerical vectors (arrays of floats) that represent the semantic meaning of the words.

### Code Breakdown

```python
from langchain_huggingface import HuggingFaceEmbeddings
```
- We import `HuggingFaceEmbeddings` from the LangChain Hugging Face integration package. This serves as a wrapper to interact with models hosted on Hugging Face.

```python
embedding_model = HuggingFaceEmbeddings(
    model= "sentence-transformers/all-mpnet-base-v2"
)
```
- We instantiate the embedding model by pointing to `sentence-transformers/all-mpnet-base-v2`.
- **Why this model?** This model is one of the standard high-quality sentence embeddings models. It converts any text block into a **768-dimensional vector**.

### Flow of the Script
1. The script is imported by other modules (like `text_chunker.py` and `ingest_documents.py`).
2. It downloads/loads the weights of the `all-mpnet-base-v2` model locally on the host machine.
3. The initialized model object is exposed as `embedding_model` to perform text encoding.

### Alternative Options
- **Alternative Embedding Models**:
  - *Cloud-Based*: OpenAI's `text-embedding-3-small` (1536 dimensions) or `text-embedding-3-large` (3072 dimensions) which require API keys.
  - *Local/Smaller*: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions), which is extremely fast and lightweight.
  - *State-of-the-Art*: `BAAI/bge-large-en-v1.5` (1024 dimensions) for superior accuracy.
- **Alternative Frameworks**:
  - Using Hugging Face's native `sentence-transformers` Python library directly instead of wrapping it via LangChain.
  - Using Ollama or llama.cpp to serve embedding endpoints locally.

---

## 2. qdrant_client.py

### What this script is
This script handles connecting to our local vector database (**Qdrant**) and initializing the collection where our document chunks will be stored. It ensures that the database environment is ready before any document ingestion takes place.

### Code Breakdown

```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
```
- We import `AsyncQdrantClient` to allow asynchronous interaction with the Qdrant DB.
- We import `Distance` and `VectorParams` which are configuration classes needed to set up collections inside Qdrant.

```python
qdrant_client = AsyncQdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "research_agent"
```
- We establish a connection to a Qdrant instance running on `localhost:6333` (typically served via a Docker container).
- We set our database table/collection name as `"research_agent"`.

```python
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
```
- **Line-by-Line Highlights**:
  - `await qdrant_client.get_collections()`: Asynchronously retrieves all collections currently residing in Qdrant.
  - `if COLLECTION_NAME not in collection_names`: We check whether the `"research_agent"` collection already exists to avoid redundant creation.
  - `vectors_config=VectorParams(size=768, distance=Distance.COSINE)`: Defines the vector settings. **`size=768`** is mandatory because it matches the output dimensions of our `all-mpnet-base-v2` embedding model. **`Distance.COSINE`** configures Qdrant to use **Cosine Similarity** to compare vector queries (which is standard and recommended for sentence-transformers).

```python
import asyncio

if __name__ == "__main__":
    asyncio.run(initialize_qdrant())
```
- An entry point that executes our asynchronous setup function using standard Python asyncio runner.

### Flow of the Script
1. Connects to the local Qdrant container at `localhost:6333`.
2. Inspects all existing collection names.
3. Checks if `"research_agent"` is missing.
4. If missing, it creates the collection configured for 768 dimensions and cosine similarity, then prints success.
5. If it already exists, it skips collection creation and outputs a status message.

### Alternative Options
- **Alternative Databases**:
  - *Local Vector DBs*: ChromaDB (extremely lightweight, runs directly in Python process memory without Docker), FAISS (fast similarity indexing engine by Meta).
  - *Cloud-Hosted DBs*: Pinecone (fully managed, zero configuration), Milvus, Weaviate.
  - *Relational DBs*: PostgreSQL with the `pgvector` extension.
- **Alternative Distance Metrics**:
  - `Distance.EUCLIDEAN` (L2 distance metric) or `Distance.DOT` (Dot Product metric).

---
