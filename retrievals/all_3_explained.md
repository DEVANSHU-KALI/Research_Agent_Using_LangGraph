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
- **Line Highlight**: We run an asynchronous vector search using Qdrant's `query_points()`. We supply the computed `query_embedding` vector and specify a search limit (`limit=3`) to retrieve only the top 3 closest items.

```python
    retrieve_chunks = []

    for point in result.points:
        retrieve_chunks.append(
            {
            'text': point.payload['text']
            }
        )
```
- We loop through the search query results, extracting the text string stored inside Qdrant's payload metadata.

```python
    context = "Local Knowledge Base:\n\n"
    context += "\n\n".join(
        chunk['text'] for chunk in retrieve_chunks
    )

    return {
        "source":"semantic",
        "context":context
    }
```
- We merge all retrieved chunks into a single text block, prefixing it with `"Local Knowledge Base:"` so the Writer LLM is aware of the source during generation.

### Flow of the Script
1. Accepts the query string from the graph state.
2. Converts the query string into a dense vector embedding.
3. Asynchronously queries the Qdrant server for the 3 most semantically similar points.
4. Loops through result payloads to construct a single structured markdown string.
5. Returns a structured dict containing the context and source label.

### Alternative Options
- **Alternative Re-ranking**: Add a Re-ranker model (like Cohere Re-rank or a local Cross-Encoder) to re-evaluate the top retrieved chunks and place the most relevant ones at the top before passing them to the generator.
- **Alternative Similarity metric**: Changing the search distance configurations inside Qdrant to Euclidean or Dot Product distance depending on model specifications.

---

## 2. internet_retrieval.py (Internet Node)

### What this script is
This script defines the **Internet Node** in our LangGraph agent. When the supervisor determines that the user's query requires current or general web knowledge, this node uses the Tavily search engine to search the web, scrape text summaries, and format them as an external search context block.

### Example Output
- **Input Query**: `"Who won the latest soccer match today?"`
- **Tavily Web Results**:
  - *Result 1*: Title: `"Soccer Scores Today"`, Content: `"Team A defeated Team B 2-1 in the final minutes."`
  - *Result 2*: Title: `"Match Analysis"`, Content: `"The match took place in London with Team A clinching victory."`
- **Returned Dictionary**:
  ```python
  {
      "source": "internet",
      "context": "Internet Search Results:\n\n**Soccer Scores Today**\nTeam A defeated Team B 2-1 in the final minutes.\n\n**Match Analysis**\nThe match took place in London with Team A clinching victory."
  }
  ```

### Code Breakdown

```python
import os
from tavily import AsyncTavilyClient

client = AsyncTavilyClient(os.getenv("TAVILY_API_KEY"))
```
- We load our Tavily API key from environment variables and initialize the `AsyncTavilyClient`.

```python
async def retrieve_internet(query: str) -> dict:
    tavily_response = await client.search(query)
```
- **Line Highlight**: We asynchronously call `client.search(query)`. Tavily is a search engine optimized for AI agents and LLMs, which means it returns structured lists of clean titles and text summaries directly instead of raw HTML garbage.

```python
    retrieved_results = []

    for result in tavily_response["results"]:
        retrieved_results.append(
            {
                'title': result["title"],
                "content": result["content"]
            }
        )
```
- We extract the title and summary contents from the JSON response list.

```python
    context = "Internet Search Results:\n\n"
    context += "\n\n".join(
        f"**{result['title']}**\n{result['content']}"
        for result in retrieved_results
    )

    return {
        "source": "internet",
        "context": context,
    }
```
- We concatenate each search result using bold headings (`**{title}**`) and group them under the `"Internet Search Results:"` header.

### Flow of the Script
1. Accepts the search query.
2. Queries the external Tavily Search API asynchronously.
3. Groups search results into a clean markdown structure containing bold titles and content paragraphs.
4. Returns the dictionary labeled with `"source": "internet"`.

### Alternative Options
- **Alternative APIs**: Serper API, Bing Search API, or Google Custom Search JSON API.
- **Alternative Scraping**: Adding Jina Reader or Firecrawl to scrape complete web page markdown if short snippets aren't detailed enough.

---
