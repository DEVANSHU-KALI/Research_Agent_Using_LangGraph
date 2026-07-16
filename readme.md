### Hybrid Research Agent built using LangGraph

This system include two retrieval methods, `Semantic retrieval` and  `Internet retrieval`. Based on specific condition, either any one selected or both work parallel, to get more information.  

- semantic retrieval is made possible using `Qdrant database` with some ingestion and retrieval logic.
- internet retrieval is done using the `Tavily Search`

Instead of building standard RAG system and combining it with internet retrieval, is used langgraph to make the system totally different from that, mainly going with this langgraph's `Map Reducer` concept, which allowed me to do this work in very reliable way and also reduced the burden of coding manually.

Each and every script and concept will be explained individually in different files.

This project can run using streamlit frontend working with fastapi backend and also using the langgraph studio which gives you a very beautiful interface to interact with the graph.


