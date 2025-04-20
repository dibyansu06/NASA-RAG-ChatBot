import json
import os
from dotenv import load_dotenv
from google import genai
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

pc = Pinecone(
        api_key=os.environ.get("PINECONE_API_KEY")
    )
index_name = "nasa-chatbot-index"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)

def load_chunks():
    with open("chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

def get_embedding(text):
    response = client.models.embed_content(
        model="models/embedding-001",
        contents=text,
        config=genai.types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return response.embeddings

def main(chunks):
    batch = []
    for chunk in chunks:
        embedding = get_embedding(chunk["content"])
        vector = {
            "id" : chunk["chunk_id"],
            "values" : embedding[0].values,
            "metadata" : {
                "source" : chunk["source"],
                "text" : chunk["content"]
            }
        }
        batch.append(vector)
        if len(batch) == 100:
            index.upsert(vectors=batch)
            batch = []
        
    if batch:
        index.upsert(vectors=batch)

    print("Process completed!")

if __name__ == "__main__":
    chunks = load_chunks()
    main(chunks)