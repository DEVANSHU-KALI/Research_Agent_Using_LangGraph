# Explanations of One-Time Scripts

This file contains the detailed explanation for all the utility scripts located in the `one_time` folder. These scripts are responsible for setting up the vector database, loading the local embedding model, chunking raw document texts semantically, and ingesting them to create a RAG knowledge base.

---

## 1. embedding_model.py

### What this script is
This script initializes our text embedding model. It loads a pre-trained model from Hugging Face using the LangChain library to convert textual strings into dense numerical vectors (arrays of floats) that represent the semantic meaning of the words.

### Code Breakdown
