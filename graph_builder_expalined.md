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
