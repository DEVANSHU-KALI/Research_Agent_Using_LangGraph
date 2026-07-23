import streamlit as st
import requests

st.title("RAG Chatbot")

# Simple input box
query = st.text_input("Ask a question")

if query:
    # Spinner displays while waiting for the first token
    with st.spinner("Server is thinking..."):
        try:
            # Call the stream endpoint with stream=True
            response = requests.get(f"http://localhost:8000/stream?query={query}", stream=True)
            
            if response.status_code == 200:
                # st.write_stream reads the text chunks and prints them typewriter-style
                st.write_stream(response.iter_content(decode_unicode=True))
            else:
                st.error(f"Error: {response.status_code}")
                
        except Exception as e:
            st.error(f"Connection failed: {e}")

if __name__ == "__main__":
    if not st.runtime.exists():
        import sys
        from streamlit.web import cli as stcli

        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
