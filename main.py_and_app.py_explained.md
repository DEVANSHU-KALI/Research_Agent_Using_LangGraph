# Explanation of Backend and Frontend Scripts

This file contains the detailed explanation for `main.py` (FastAPI backend) and `app.py` (Streamlit frontend), focusing specifically on real-time token streaming and reflection monitoring.

---

## 1. What these Scripts Do & Why they are Needed
In a standard RAG system, the user submits a question and wait. Because our system includes a **self-reflection loop** (where the answer can be rewritten up to 5 times), this wait time can easily exceed 10 to 15 seconds. If the UI is static, the user might assume the system has crashed.

To solve this:
- **`main.py` (Backend)**: Exposes a `/stream` API endpoint. Instead of waiting for the graph to finish, it taps into LangGraph's internal events and streams LLM tokens to the client as they are generated.
- **`app.py` (Frontend)**: Connects to the backend via a streaming HTTP request. It consumes the incoming text stream and displays it typewriter-style in real time.
