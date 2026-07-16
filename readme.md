### Hybrid Research Agent built using LangGraph

This system include two retrieval methods, `Semantic retrieval` and  `Internet retrieval`. Based on specific condition, either any one selected or both work parallel, to get more information.  

- semantic retrieval is made possible using `Qdrant database` with some ingestion and retrieval logic.
- internet retrieval is done using the `Tavily Search`

Instead of building standard RAG system and combining it with internet retrieval, is used langgraph to make the system totally different from that, mainly going with this langgraph's `Map Reducer` concept, which allowed me to do this work in very reliable way and also reduced the burden of coding manually.

Each and every script and concept will be explained individually in different files.

This project can run using streamlit frontend working with fastapi backend and also using the langgraph studio which gives you a very beautiful interface to interact with the graph.

---

### How to run
No matter what way you go with, you need to start the qdrant database lying in the docker container if you have it inside that. so ets start with the ingestion stage.

First run:
```bash
pip install -e .
```
- this installs all the required libraries and all. 

#### Ingestion stage.
- you have two way, either get the qdrant database directly into you system or get that as a docker container. To get the container way, start your dockers application, let the engine start, then run the command:
```bash
docker compose up -d
```
- wait for some time, this will create and install qdrant in you dockers.
- after some time, you will see some message like, containers created. you may see something like:
```bash
✔ Network docker_default   Created             0.0s
✔ Container qdrant_db      Created             0.1s
```
- This tells you qdrant database has started.
- By default qdrant runs on localhost 6333 port, so you can go directly into the webpage and enter:
```text
http://localhost:6333/dashboard#/collections
```
- this will take you to the collection portal of the database where you can see your collections get created later in the process.

After getting this work done, run the command:
```bash
python -m .\one_time\qdrant_client
```
- this will create collection naming `research_agent` as its mentioned in the qdrant_client script.

Next comes the final step of ingestion, to push data into the collection. Run the following command:
```bash
python -m .\one_time\ingest_documents
```

#### to get streamlit frontend
- we need to start both the backend and 