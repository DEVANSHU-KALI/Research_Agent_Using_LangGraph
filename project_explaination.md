This file is going to explain the connection between the individual scripts and the flow.

To understand this project, you need some of the knowledge about langgraph, you need to know the basics. I've created another repository in my git hub account `DEVANSHU-KALI` naming `Learn_LangGraph`. There is a readme file which tells the basic concept of langgraph, so you can understand the terminology used here.

## State: shred clipboard
observer the graph_builder script
```python
class my_state(TypedDict):
    query: str
    decision: NotRequired[str]
    retrieval_results: Annotated[list[dict], operator.add]
    final_answer: NotRequired[dict]
    feedback: NotRequired[str]
    iteration_count: NotRequired[int]
    review_status: NotRequired[str]
```
- **query**: passed by the users from the frontend which is just a string so we pass `str` as the type.
- **decision**: the value for this key is decided by the     supervisor node, where there are three decisions, `semantic`, `internet` and `hybrid`, all three of string type. 
    - if `semantic` is the decision: the query is passed to semantic node.
    - if `internet`: internet node gets the query 
    - if `hybrid`: we use the concept of `map-reduce` to send query to both the `semantic` and `internet` nodes and make them parallelly, and update the `retrieval_results` key.
- **retrieval_results**: either `semantic` or `internet` or in case of `hybrid` both the nodes, based on decision will updated this key with their response.
    - we return source and context from each node, which is captured by the variable 'retrieval_results' and update that **retrieval_results** key.
    - don't get confused, both the key in the state and variable names are same. see the graph_builder script, you can understand there, in node functions. 
