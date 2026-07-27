# Explanations of Retrieval Scripts

This file contains the detailed explanation for all the scripts located in the `retrievals` folder. These scripts govern how the system fetches reference data, utilizing local vector search, public web scraping, or both.

---

## 1. semantic_retrieval.py (Semantic Node)

### What this script is
This script defines the **Semantic Node** in our LangGraph agent. It takes the user's query, converts it into a high-dimensional vector representation, executes a similarity search against our local Qdrant database, and retrieves the top 3 most relevant document chunks to format them as local knowledge context.

### Example Output
- **Input Query**: `"What is quantum physics?"`
- **Matched database chunks**:
  - *Chunk 1*: `"Quantum physics is the study of matter and energy at the most fundamental level."`
  - *Chunk 2*: `"Key principles of quantum physics include superposition and entanglement."`
  - *Chunk 3*: `"Max Planck is considered the father of quantum theory."`
- **Returned Dictionary**:
  ```python
  {
      "source": "semantic",
      "context": "Local Knowledge Base:\n\nQuantum physics is the study of matter and energy at the most fundamental level.\n\nKey principles of quantum physics include superposition and entanglement.\n\nMax Planck is considered the father of quantum theory."
  }
  ```

### Code Breakdown

```python
from one_time.qdrant_client import qdrant_client, COLLECTION_NAME
from one_time.embedding_model import embedding_model
```
- We import our initialized local Qdrant client connection, target collection name, and the embedding model module from our setup files.

```python
async def retrieve_chunks(query: str) -> dict:
    query_embedding =  embedding_model.embed_query(query)
```
- **Line Highlight**: `embed_query(query)` is a specific method that embeds the single user query string into a 768-dimension vector. *(Note: This is different from `embed_documents()` which is used to process a list of multiple strings in batch).*

```python
    result = await qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit = 3
    )
```