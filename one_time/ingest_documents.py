from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import os
from one_time.embedding_model import embedding_model
from one_time.text_chunker import text_splitter

COLLECTION_NAME = "research_agent"

client = QdrantClient(host="localhost", port=6333)

def ingest_documents(folder_path: str) -> None:
    documents = []
    chunk_id = 0

    # read text file from the 
    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue
        
        file_path = os.path.join(folder_path, filename)

        with open (file_path, "r", encoding="utf-8") as file:
            text = file.read()
        
        # creating chunks from text
        chunks = text_splitter.create_documents([text])

        for chunk in chunks:
            documents.append(
                {'chunk_id':chunk_id, 'text': chunk.page_content}
            )

            chunk_id += 1       

    # generate embeddings
    chunk_texts = [document["text"] for document in documents]
    
    embeddings = embedding_model.embed_documents(chunk_texts)

    print(f"Generated {len(documents)} chunks")

    #create qdrant points
    points = []

    for document, embedding in zip(documents, embeddings):
        points.append(
            PointStruct(
                id = document["chunk_id"],
                vector = embedding,
                payload= {
                    "chunk_id": document["chunk_id"],
                    "text": document["text"]
                }
            )
        )

    # uploading points to qdrant
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    
    print(f"Uploaded {len(points)} chunks to Qdrant")


if __name__ == "__main__":
    ingest_documents("data")
