# Explanations of Retrieval Scripts

This file contains the detailed explanation for all the scripts located in the `retrievals` folder. These scripts govern how the system fetches reference data, utilizing local vector search, public web scraping, or both.

---

## 1. semantic_retrieval.py (Semantic Node)

### What this script is
This script defines the **Semantic Node** in our LangGraph agent. It takes the user's query, converts it into a high-dimensional vector representation, executes a similarity search against our local Qdrant database, and retrieves the top 3 most relevant document chunks to format them as local knowledge context.

### Example Output
- **Input Query**: `"What is quantum physics?"`
- **Matched database chunks**:
  - *Chunk 1*: `"Quantum physics is the study of matter and energy at the most fundamental level."`
  - *Chunk 2*: `"Key principles of quantum physics include superposition and entanglement."`
  - *Chunk 3*: `"Max Planck is considered the father of quantum theory."`
- **Returned Dictionary**:
  ```python
  {
      "source": "semantic",
      "context": "Local Knowledge Base:\n\nQuantum physics is the study of matter and energy at the most fundamental level.\n\nKey principles of quantum physics include superposition and entanglement.\n\nMax Planck is considered the father of quantum theory."
  }
  ```
