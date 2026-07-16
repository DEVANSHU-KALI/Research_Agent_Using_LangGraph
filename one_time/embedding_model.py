from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model= "sentence-transformers/all-mpnet-base-v2"
)