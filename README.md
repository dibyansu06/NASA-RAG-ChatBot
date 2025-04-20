# 🚀 NASA RAG Chatbot

An intelligent chatbot that answers questions about NASA, space science, and astronomy using Retrieval-Augmented Generation (RAG) and real-time NASA APIs.

## 🔍 Features
- 🔗 LLM + LangChain for dynamic query classification & context retrieval
- 📄 Per-file FAISS vector search on user PDFs + NASA doc retrieval via Pinecone
- 🌐 Real-time integration with NASA APIs (APOD, NeoWs, Earth Imagery)
- 👤 Google OAuth, user sessions, memory-based chat history, and file uploads

## 🧠 Tech Stack
- **Backend**: Django, LangChain, Gemini API
- **Vector DBs**: FAISS (local), Pinecone (NASA KB)
- **Frontend**: HTML, Tailwind CSS
- **Auth**: Google OAuth2

## 🛠️ Setup Instructions

```bash
git clone https://github.com/dibyansu06/NASA-RAG-ChatBot.git
cd backend/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

