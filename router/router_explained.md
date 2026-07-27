# Explanation of Router Scripts

This file contains the detailed explanation for the routing logic used to steer incoming user questions into the correct retrieval path.

---

## query_router.py (Supervisor Node)

### What this script is
This script defines the **Supervisor Node** (or Router) in our LangGraph architecture. Its purpose is to evaluate the user's question and decide the most cost-effective and accurate retrieval strategy to get the answer. 

#### Why does this routing logic exist?
In a production RAG application, sending every single query to both your local vector database and the web search API is slow, expensive (wasting tokens), and cluttering. For instance:
- If a user asks *"What is our company's refund policy?"*, the internet cannot answer it. We only need the **semantic** local database.
- If a user asks *"What is the weather today?"*, the local files cannot answer it. We only need **internet** search.
- The router serves as a gatekeeper that classifies the query, deciding to run only what is necessary.

---

### Critical Concept: The Double Brackets `{{` and `}}` in Prompting

If you inspect the long supervisor prompt, you will notice that JSON example snippets are wrapped in double brackets, like:
```python
Question:
"What is our leave policy?"
Output:
{{"decision": "semantic"}}
```
