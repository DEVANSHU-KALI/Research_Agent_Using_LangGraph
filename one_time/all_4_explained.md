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

## 3. text_chunker.py

### What this script is
This script defines our document chunking strategy. Before sending large documents to a vector database, they must be split into smaller, manageable text pieces. Rather than using arbitrary split counts, this script employs a **Semantic Chunker** that detects natural shifts in meaning to create chunks.

### Code Breakdown

```python
from langchain_experimental.text_splitter import SemanticChunker
from one_time.embedding_model import embedding_model
```
- We import `SemanticChunker` from LangChain's experimental modules.
- We import the `embedding_model` we initialized in `embedding_model.py`. The semantic chunker uses this model to calculate how closely related adjacent sentences are.

```python
text_splitter =  SemanticChunker(
    embedding_model,
    breakpoint_threshold_type= 'percentile',
    breakpoint_threshold_amount= 75
)
```
- **How it works**:
  - The chunker parses the document into sentences and embeds each sentence.
  - It measures the semantic difference between consecutive sentences.
  - `breakpoint_threshold_type='percentile'` with `breakpoint_threshold_amount=75` instructs the chunker to split the text at sentences where the semantic distance difference falls in the top 25% (greater than the 75th percentile of differences across the document). This creates boundaries where the topic actually shifts.

### Flow of the Script
1. Reads `embedding_model` configuration.
2. Initializes the `SemanticChunker` instance with embedding analysis and percentile parameters.
3. Exposes the configured `text_splitter` instance for document loaders to import and invoke.

### Alternative Options
- **Alternative Chunking Splitters**:
  - `RecursiveCharacterTextSplitter`: Splits text based on raw characters (like double newlines `\n\n`, single newlines `\n`, spaces) down to a specific size (e.g., 500 characters chunk size, 50 characters overlap). It is much faster but lacks topic awareness.
  - `CharacterTextSplitter`: Splits strictly on specific character occurrences.
  - *Token-based Splitters*: Splitting by exact Token limits (e.g., using `tiktoken` helper) to guarantee chunks never overflow the LLM's context windows.

---

## 4. ingest_documents.py

### What this script is
This is the document ingestion pipeline. It reads all raw `.txt` files from a target directory, breaks them down using our semantic splitter, translates each chunk into a 768-dimension vector embedding, and uploads them (along with original text data) as searchable points into Qdrant.

### Code Breakdown

```python
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
from one_time.embedding_model import embedding_model
from one_time.text_chunker import text_splitter

COLLECTION_NAME = "research_agent"

client = QdrantClient(host="localhost", port=6333)
```
- We import the synchronous `QdrantClient` for simple bulk ingestion, and `PointStruct` which is the data format that Qdrant expects for uploads.
- We connect to Qdrant at `localhost:6333`.

```python
def ingest_documents(folder_path: str) -> None:
    documents = []
    chunk_id = 0

    # read text file from the 
    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue
        
        file_path = os.path.join(folder_path, filename)

        with open (file_path, "r", encoding="utf-8") as file:
            text = file.read()
```
- We loop through the files inside the target directory (`data`), filtering out any non-txt files, and reading their text content.

```python
        # creating chunks from text
        chunks = text_splitter.create_documents([text])

        for chunk in chunks:
            documents.append(
                {'chunk_id':chunk_id, 'text': chunk.page_content}
            )
            chunk_id += 1       
```
- We call `text_splitter.create_documents([text])` to split the raw string into semantic chunk documents.
- We assign a unique incremental `chunk_id` to each chunk and store them inside the `documents` list.

```python
    # generate embeddings
    chunk_texts = [document["text"] for document in documents]
    embeddings = embedding_model.embed_documents(chunk_texts)
```
- We isolate all chunk text strings into a list.
- We call `embedding_model.embed_documents()` to generate the dense vector representation for each chunk in a single batch.
