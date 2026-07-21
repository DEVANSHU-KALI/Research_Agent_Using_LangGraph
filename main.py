import os 
from dotenv import load_dotenv
# Load env variables from parent folder before importing local graph modules
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from graph_builder import graph

app = FastAPI(title="Research Agent API")

# Configure CORS Middleware
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501,http://127.0.0.1:8501")
origins = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class QueryRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    # 1. Run the Graph
    result = await graph.ainvoke({"query": request.prompt})
    
    # 2. Extract final answer and the iteration counter from the state
    final_answer = result.get("final_answer", {}).get("answer", "No answer generated.")
    iter_count = result.get("iteration_count", 1)
    
    # 3. Print log to the server console
    print(f"\n--- [COMPLETED] Response generated in {iter_count} iteration(s) ---")
    
    # 4. Return answer + iteration count to the client
    return {
        "answer": f"{final_answer}\n\n*(Generated in {iter_count} iteration(s))*"
    }

@app.get("/stream")
async def stream_endpoint(query: str):
    async def generate():
        iter_count = 1
        async for event in graph.astream_events({"query": query}, version="v2"):
            # Token Streaming logic (unchanged)
            if event.get("event") == "on_chat_model_stream":
                if event.get("metadata", {}).get("langgraph_node") == "Writer":
                    token = event.get("data", {}).get("chunk", {}).content
                    if token:
                        yield token
            
            # NEW: Listen for when the Writer node completes a run
            elif event.get("event") == "on_node_end":
                if event.get("name") == "Writer":
                    state_output = event.get("data", {}).get("output", {})
                    iter_count = state_output.get("iteration_count", iter_count)

        print(f"\n--- [COMPLETED] Stream finished (Iterations: {iter_count}) ---")
        yield f"\n\n*(Generated in {iter_count} iteration(s))*"

    return StreamingResponse(generate(), media_type="text/plain")
 
if __name__ == "__main__":
    import uvicorn
    # Programmatic entry point to run uvicorn server directly using python
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)