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
4. **Future changes**: If you want to go and change any node or anything it would be easier than just scrolling the single graph builder script.

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
- The next three imports are used in the below scripts for some specific work.
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
- All the other keys are simple to understand, the only thing here to understand here is about the concept **Map Reducers**, explained below:
- **The Reducer (`operator.add`)**:
  - By default, LangGraph overwrites state keys with the latest node's return dictionary.
  - For `retrieval_results`, we use `Annotated[list[dict], operator.add]`. This configuration tells LangGraph: *"Instead of overwriting this list, append new results to it."*
  - This is vital when we run **parallel retrievals (Map-Reduce)** so that both nodes can write to the state concurrently without data loss.
  - In simple words, when the decision is `hybrid`, we run both the nodes parallelly, in normal condition, the first very first retrieval which completed its work and updated the state's key would be the final, but we don't that to happen right, so we use this `operator.add` which will just append the new retrieval's result to the list in which we already have some info present.
  - when you think about adding concept, keep a eye on what `type` you are assigning to the value, it should be a list mainly, and its your choice about what you need inside that list.

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

```python
async def writer_node(state: my_state):
    current_iter = state.get('iteration_count', 0) + 1
    feedback = state.get('feedback', "")
    final_answer = await writer(state['query'], state.get('retrieval_results', []), feedback)
    return {
        'final_answer': final_answer,
        'iteration_count': current_iter
    }
```
- Increments the loop tracker (`iteration_count`).
- Reads the latest `feedback` (if any exists from a previous review).
- Calls the writer node to synthesize a response, updating `final_answer`.

```python
async def reviewer_node(state: my_state):
    review_result = await review_answer(
        state['query'],
        state['final_answer']['answer'],
        state.get('retrieval_results', [])
    )
    return {
        'review_status': review_result['status'],
        'feedback': review_result['feedback']
    }
```
- Passes the question, generated answer, and reference context to the reviewer.
- Updates the quality checks status (`review_status` as `"pass"` or `"fail"`) and `feedback` instructions.

---

### Step 3.4: Conditional Routing & Loop Guard

```python
def route_query(state: my_state):
    decision = state['decision']
    if decision == 'hybrid':
        return ['semantic', 'internet']
    return [decision]
```
- **Parallel Fan-Out**: If the supervisor returns `"hybrid"`, this routing function returns a list containing both retrieval node names: `['semantic', 'internet']`. This instructs LangGraph to spin up both nodes in parallel.

```python
def route_review(state: my_state):
    status = state.get('review_status', 'pass')
    iter_count = state.get('iteration_count', 0)
    
    # Loop Guard
    if iter_count >= 5 and status == 'fail':
        print("--- [LOOP GUARD] Forced Exit after 5 iterations ---")
        return "pass"  # Go to END
        
    if status == 'pass' or iter_count >= 5:
        return "pass"  # Go to END
        
    return "fail"  # Go to Writer
```
- **Loop Guard / Self-Reflection Routing**:
  - If the answer fails review checks, it returns `"fail"`, looping back to the **Writer** node.
  - If it passes, it returns `"pass"`, routing execution to the `END`.
  - **Loop Guard**: If `iter_count >= 5`, it overrides the failing status and routes directly to the `END`. This prevents the agent from getting stuck in an infinite loop of generative refinement, saving API costs and execution timeouts.

---

### Step 3.5: Wiring the Graph

```python
builder.add_node("Supervisor", supervisor_node)
builder.add_node('Semantic', semantic_node)
builder.add_node('Internet', internet_node)
builder.add_node('Writer', writer_node)
builder.add_node('Reviewer', reviewer_node)

builder.add_edge(START, "Supervisor")
```
- We register each node under a unique string name and link the start of the state machine directly to the Supervisor.

```python
builder.add_conditional_edges(
    'Supervisor',
    route_query,
    {
        "semantic": "Semantic",
        "internet": "Internet",
    },
)
```
- Conditional route exiting the Supervisor: mapping the returning choices of `route_query` to their respective nodes.

```python
builder.add_edge("Semantic", "Writer")
builder.add_edge("Internet", "Writer")
builder.add_edge("Writer", "Reviewer")

builder.add_conditional_edges(
    'Reviewer',
    route_review,
    {
        "pass": END,
        "fail": "Writer",
    }
)

graph = builder.compile()
```
- Standard edges connecting the retrieval outputs directly into the Writer, and the Writer into the Reviewer.
- Conditional edge exiting the Reviewer to decide whether to terminate (go to `END`) or loop back to `"Writer"`.
- We call `builder.compile()` to convert the layout configuration into a runnable state machine.

---

## 4. Execution Flow Diagram

Here is how data moves dynamically inside the compiled state machine:

```
                  [START]
                     │
                     ▼
             ┌───────────────┐
             │  Supervisor   │ ──► Sets decision
             └───────────────┘
                     │
         ┌───────────┼───────────┐
         │ (semantic)│ (internet)│ (hybrid - runs both)
         ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌───────────────┐
   │ Semantic │ │ Internet │ │ Run Parallel  │
   └──────────┘ └──────────┘ └───────────────┘
         │           │               │
         └───────────┼───────────────┘
                     │  (Appends to retrieval_results)
                     ▼
             ┌───────────────┐ ◄───┐
             │    Writer     │     │
             └───────────────┘     │ (loops back if fail)
                     │             │
                     ▼             │
             ┌───────────────┐     │
             │   Reviewer    │ ────┘
             └───────────────┘
                     │
             ┌───────┴───────┐
             │ (pass / max)  │ (fail & iter < 5)
             ▼               ▼
           [END]         (Loop back)
```
