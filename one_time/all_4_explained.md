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
