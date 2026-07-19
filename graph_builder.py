from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from typing_extensions import NotRequired
import operator

from router.query_router import supervisor
from retrievals.semantic_retrieval import retrieve_chunks
from retrievals.internet_retrieval import retrieve_internet
# Import generate_answer and alias it as 'writer' to keep the graph naming clean
from generation.generator import generate_answer as writer
from generation.reviewer import review_answer  # Import reviewer

# Define state schema with feedback and loop counter keys
class my_state(TypedDict):
    query: str
    decision: NotRequired[str]
    retrieval_results: Annotated[list[dict], operator.add]
    final_answer: NotRequired[dict]
    feedback: NotRequired[str]
    iteration_count: NotRequired[int]
    review_status: NotRequired[str]

builder = StateGraph(my_state)

# --- nodes ---
async def supervisor_node(state: my_state):
    res = await supervisor(state['query'])
    return {
        'decision': res['decision']
    }

async def semantic_node(state: my_state):
    retrieval_results = await retrieve_chunks(state['query'])
    return {
        'retrieval_results': [retrieval_results]
    }   

async def internet_node(state: my_state):
    retrieval_results = await retrieve_internet(state['query'])
    return {
        'retrieval_results': [retrieval_results]
    }

async def writer_node(state: my_state):
    # Track the current iteration loop count
    current_iter = state.get('iteration_count', 0) + 1
    
    # Retrieve previous review feedback if it exists
    feedback = state.get('feedback', "")
    
    # Call the local generator with feedback awareness
    final_answer = await writer(state['query'], state.get('retrieval_results', []), feedback)
    
    return {
        'final_answer': final_answer,
        'iteration_count': current_iter
    }

async def reviewer_node(state: my_state):
    # Call the reviewer node
    review_result = await review_answer(
        state['query'],
        state['final_answer']['answer'],
        state.get('retrieval_results', [])
    )
    return {
        'review_status': review_result['status'],
        'feedback': review_result['feedback']
    }

# -- node registration ---
builder.add_node("Supervisor", supervisor_node)
builder.add_node('Semantic', semantic_node)
builder.add_node('Internet', internet_node)
builder.add_node('Writer', writer_node)
builder.add_node('Reviewer', reviewer_node)  # Register Reviewer

# --- edges & routing ---
def route_query(state: my_state):
    decision = state['decision']
    if decision == 'hybrid':
        return ['semantic', 'internet']
    return [decision]

def route_review(state: my_state):
    status = state.get('review_status', 'pass')
    iter_count = state.get('iteration_count', 0)
    
    # RULE 1: Did we hit the 5-try limit with a failing answer?
    # Print the warning and exit to END.
    if iter_count >= 5 and status == 'fail':
        print("--- [LOOP GUARD] Forced Exit after 5 iterations ---")
        return "pass"  # Go to END
        
    # RULE 2: Did the answer pass, or did we hit the limit?
    # Exit to END (no warning needed).
    if status == 'pass' or iter_count >= 5:
        return "pass"  # Go to END
        
    # RULE 3: The answer failed, but we still have tries left.
    # Loop back to Writer.
    return "fail"  # Go to Writer

builder.add_edge(START, "Supervisor")

builder.add_conditional_edges(
    'Supervisor',
    route_query,
    {
        "semantic": "Semantic",
        "internet": "Internet",
    },
)

builder.add_edge("Semantic", "Writer")
builder.add_edge("Internet", "Writer")
builder.add_edge("Writer", "Reviewer")  # Route to Reviewer

# Conditional edge from Reviewer (decides whether to pass to END or loop to Writer)
builder.add_conditional_edges(
    'Reviewer',
    route_review,
    {
        "pass": END,
        "fail": "Writer",
    }
)

graph = builder.compile()
# TODO: 
# add another node naming reviewer.
# max 5 times. 
# there should be a loop. "reflection". 
# pass or fail. if pass no need of feedback. if fail, write a conditional edge to writer  node. for the 5th time the route should be end, no matter what is the final answer from the writer node. 

# FIXME: 


# what is the concept of map reducer works?
# first thing, dont mixup the two terms. map refers to mapping, where we execute some parallel edge and get some results.
# at the same time, reducer is which combines the results from both the nodes connected parallelly. 
# ---
# now lets know how is that working with the code!!
# the task is not about understanding how the paralledl edge is created, its mostly about how the reducer works there.
# its all possible by that single term "operator.add" added to specific key's type of the state, so that the state wouldn't overwrite the updated made to that key and reserve the changes.
# you can see the example in the line: 16. 
# now about the parallel edge, for this we need to define what condition should trigger the parallel execution, spin up the two parallel nodes.
# for us the the condition was the llm returning hybrid as the decision. so for that we write a function in the pre phase of edge creation, as python executes the code from top to bottom.
# function in the line: 54. has some simple if logic, which returns both the retrieval nodes in a list, which tells the system to execute both the nodes paralelly.
# how is that parallel edge is triggered?, this is the final step, see the line 64, where we started to write the logic for the conditional edging.
# if the result is hybrid, we know what happens, so for conditional edge, we simply add the function we wrote with the supervisor node. so the condition stays next after the supervisor node.
# ---
# one thing to know when we are using this reducing concept is, we need to be careful with what are we are returning. our system worked because, we wrapped all the node's results in a list, as mentioned in line 16, as we gave list[dict]

#TODO: need to go though the whole website, and check if are there any changes to made.
#TODO: work on voice box which can clone voice. 