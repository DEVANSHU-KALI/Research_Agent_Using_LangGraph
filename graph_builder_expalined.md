# Explanation of Graph Builder Script

This file contains the detailed explanation for `graph_builder.py`. It is the central orchestrator (the "brain") of the entire project, defining our state machine, routing conditions, node connections, and execution flow using LangGraph.

---

## 1. Why this Script is Needed & What it Does
In complex AI applications, we need a way to connect different tasks—like query routing, data searching, content writing, and quality review—into a structured workflow that can loop, self-correct, or run tasks in parallel. 

`graph_builder.py` does exactly this:
- It defines a **State Schema** that acts as a shared clipboard.
- It sets up **Nodes** (which perform actions).
- It wires **Edges** (which define the flow between nodes).
- It sets up **Conditional Edges** (to route or loop based on evaluation results).
- It compiles everything into a single executable object (`graph`).

---

## 2. Key Architectural Feature: Decoupled Node Logic

Most basic LangGraph tutorials show a monolithic layout: developers write the complete logic (prompts, API client queries, text formatting) directly inside the node functions in one massive file. 

Our project uses a **modular architecture** (Separation of Concerns):
- The core implementation logic is stored in separate modular folders: `/router`, `/retrievals`, and `/generation`.
- `graph_builder.py` **only** imports these pure execution functions (like `supervisor`, `retrieve_chunks`, `writer`, `review_answer`).
- Inside `graph_builder.py`, we write short, clean **wrapper functions** (e.g. `async def semantic_node(state)`) that read inputs from the graph state, call the imported logic, and return updates to the state.

#### Why is this better?
1. **Clean Code**: The graph layout remains easily readable.
2. **Reusability**: You can call the retrieval and generation scripts independently for unit testing or command-line scripts without spinning up the whole graph.
3. **Easy Maintenance**: If you need to change a prompt, you edit it in its respective folder, not inside the complex graph orchestrator.

---

## 3. Code Breakdown

### Step 3.1: Imports and Client Logic

```python
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from typing_extensions import NotRequired
import operator

from router.query_router import supervisor
from retrievals.semantic_retrieval import retrieve_chunks
from retrievals.internet_retrieval import retrieve_internet
from generation.generator import generate_answer as writer
from generation.reviewer import review_answer
```
- We import LangGraph's core layout structures (`StateGraph`, `START`, `END`).
- We import modular functions from our packages to delegate execution tasks. Notice that we alias `generate_answer as writer` to keep graph names clean and intuitive.

---

### Step 3.2: State Schema with Reducer

```python
class my_state(TypedDict):
    query: str
    decision: NotRequired[str]
    retrieval_results: Annotated[list[dict], operator.add]
    final_answer: NotRequired[dict]
    feedback: NotRequired[str]
    iteration_count: NotRequired[int]
    review_status: NotRequired[str]

builder = StateGraph(my_state)
```
- **The Reducer (`operator.add`)**:
  - By default, LangGraph overwrites state keys with the latest node's return dictionary.
  - For `retrieval_results`, we use `Annotated[list[dict], operator.add]`. This configuration tells LangGraph: *"Instead of overwriting this list, append new results to it."*
  - This is vital when we run **parallel retrievals (Map-Reduce)** so that both nodes can write to the state concurrently without data loss.

---

### Step 3.3: Node Wrapper Functions

Each wrapper function acts as an interface between LangGraph's state and our modular scripts:

```python
async def supervisor_node(state: my_state):
    res = await supervisor(state['query'])
    return {'decision': res['decision']}
```
- Reads the `query` string, executes routing classification, and updates the `decision` state key.

```python
async def semantic_node(state: my_state):
    retrieval_results = await retrieve_chunks(state['query'])
    return {'retrieval_results': [retrieval_results]}
```
- Executes local database vector search. Note that the result is wrapped inside a list `[retrieval_results]` to match the list expectations of our `operator.add` state reducer.

```python
async def internet_node(state: my_state):
    retrieval_results = await retrieve_internet(state['query'])
    return {'retrieval_results': [retrieval_results]}
```
- Performs a live web search and wraps result in a list.
