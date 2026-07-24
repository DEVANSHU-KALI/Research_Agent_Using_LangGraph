These two file hold the logic for two nodes used in the graph. Let's see all the how they work.

## generator.py (writer node)
- This node has two different works related to generating response.
    - One: generate response normally
    - Two: in case of the response gets `fail`, consider that `feedback` provided by the `reviewer node` and regenerate the response.
        - small note: as per the project architecture, even if the second response gets failed, similarly with the 4 more response get failed, no matter what the 6th response gets, its considered as final response. all the information is mentioned in the `readme` and `project_explainnation` md files 
- This node takes the retrieved_results (context) from any two of retrieval methods and generates a response which looks far better than raw llm output, as the prompt is designed in such way.
- The prompt used in this script will, add emojis to the response, make that response look professional and also like making a notes of it.


### code breakdown

```python
from langchain_openai import ChatOpenAI
import os

llm_model = ChatOpenAI(
model="llama-3.1-8b-instant",
base_url="https://api.groq.com/openai/v1",
api_key=os.getenv("GROQ_API_KEY")
)
```
- import chatopenai to get the better response format, you can also go with other type of formats (gemini sdk, calude, etc).
- I've used the `llama` model from the `Groq` llm provider, you can use any model you want, just add the api key in the env file, configure the chat endpoint and mention the model here.

```python 

async def generate_answer(query: str, retrieval_results: list[dict], feedback: str = "") -> dict:
    # 1. Merge the list of contexts from all executed retrieval nodes
    contexts = [res["context"] for res in retrieval_results]
    merged_context = "\n\n".join(contexts)
```
- As mentioned, this function takes the 
    - `query`
    - `retrieval_results` from the retrievals methods
    - `feedback` only in case of `fail`, and thats the reason why, it is kept null by default. code:`str = ""` (tells, it should be string and by default its null)
- In case of supervisor node classifies the query to `hyrbrid` retrieval, both the `semantic` and `internet` are ran **parallelly**, which updates the `retrieval_result` key with two **contexts**, and to get that context 
merged properly seperated by some space, we get that logic here.
#### example:
- lets say we have the context as:
```python
retrieval_results = [
    {
        "source": "semantic",
        "context": "LangGraph is a library for building stateful agent workflows."
    },
    {
        "source": "internet",
        "context": "According to the web, LangGraph was released by LangChain."
    }
]
```
- with the merging it would look like:
```python
contexts = [
    "LangGraph is a library for building stateful agent workflows.",
    "According to the web, LangGraph was released by LangChain."
]
```

> Note: this is only possible because, this graph has the concept of map-reduce, where we take even if one retrieval state updates the key with its context, the second retrieval method's context gets appended to the list. 

```python
    feedback_instruction = ""
    if feedback:
        feedback_instruction = f"\n\nCRITICAL FEEDBACK ON PREVIOUS RESPONSE:\nThe reviewer rejected your last response with this critique:\n\"{feedback}\"\nRead this feedback carefully and completely resolve the issue in your new answer."
```
- As the reviewer nodes gives a feedback in case of fail, this is the prompt we got and is combined with the main prompt sent to the llm.

Next we have the main prompt, which takes query and merged context with feedback (option).

```python 
response = await llm_model.ainvoke([prompt])

    return {
        'answer': response.content,
    }
```
- Lastly we pass the prompt to the llm and return the response.

---

## reviewer.py

