import os 
import json
from google import genai
from pinecone import Pinecone
from dotenv import load_dotenv
from utils.embed_and_store import get_embedding
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from .nasa_api import call_nasa_api
from .gemini_classifier import classify_and_extract

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

pc = Pinecone(
        api_key=os.environ.get("PINECONE_API_KEY")
    )
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def embed_pdf(pdf_path, user_id):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(pages)

    embeddings = HuggingFaceEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    filename = Path(pdf_path).stem
    output_dir = f"vectorstores/user_{user_id}/{filename}_index"
    os.makedirs(output_dir, exist_ok=True)
    vectorstore.save_local(output_dir)


def retrieve_pinecone_chunks(query, top_k=5):
    query_embedding = get_embedding(query)[0].values
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return [match["metadata"]['text'] for match in results["matches"]]

def retrieve_user_chunks(query, user_id, top_k=5):
    base_path = f"vectorstores/user_{user_id}"
    if not os.path.exists(base_path):
        return []
    
    embeddings = HuggingFaceEmbeddings()
    all_results = []

    for folder in os.listdir(base_path):
        index_path = os.path.join(base_path, folder)
        if os.path.isdir(index_path):
            try:
                vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
                results = vectorstore.similarity_search(query, k=top_k)
                all_results.extend(results)
            except Exception as e:
                print(f"Error loading index from {index_path} : {e}")
    return [doc.page_content for doc in all_results[:top_k]]


def format_context(user_chunks, nasa_chunks):
    context = ""
    if user_chunks:
        context += "User document chunks:\n" + "\n".join(user_chunks) + "\n\n"
    if nasa_chunks:
        context += "Retrieval document chunks:\n" + "\n".join(nasa_chunks) 
    return context

def generate_answer(question, context, memory):    
    prompt = f"""You are a NASA assistant. Use the conversation history and documents below to answer the user's question.
    
    Conversation History:
    {memory}
    
    {context}

    User: {question}
    Assistant:"""
    
    response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
    return response.text.strip()

def format_nasa_api_response(api, data):
    if api == "apod":
        print(f"**{data.get('title', "Astronomy Picture of the Day")}**\n\n{data.get('explanation', "")}\n\n![Image]({data.get('url', "")})")
        return f"**{data.get('title', "Astronomy Picture of the Day")}**\n\n{data.get('explanation', "")}\n\n![Image]({data.get('url', "")})"
    if api == "earth":
        image_url = data.get('url', "")
        return f"Earth imagery caputred:\n\n![Earth Image]({image_url})"
    
    return "Here's the reuslt from NASA API:\n" + json.dumps(data, indent=2)

def get_rag_response(question, memory, user_id):
    sample_user_chunks = retrieve_user_chunks(question, user_id)
    sample_text = "\n".join(sample_user_chunks)

    classification = classify_and_extract(question, sample_text, client)
    source = classification.get("source")
    api = classification.get('api')
    params = classification.get("params", {})
    print("get_rag_response", source, api, params)

    user_chunks = sample_user_chunks if source in ["user", "both"] else []
    nasa_chunks = retrieve_pinecone_chunks(question) if source in ["nasa", "both"] else []

    context = format_context(user_chunks, nasa_chunks)
    response = ""
    if not api:
        response = generate_answer(question, context, memory)
    
    return {
        "response" : response,
        # "context"  : context,
        "api" : api,
        "params" : params
    }



### -----------------------------------

# parse the neows response properly!!!!!!!
# call 2nd llm for neows
# also mention that the relevant information is shared in a table below

### -----------------------------------