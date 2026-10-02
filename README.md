# MediChat AI

MediChat AI is an AI-powered healthcare chatbot that uses Retrieval-Augmented Generation (RAG) to provide context-aware responses based on healthcare-related documents.

## Features

- AI-powered healthcare question answering
- Retrieval-Augmented Generation (RAG)
- Semantic document search
- Medical document ingestion
- FAISS-based vector search
- Context-aware responses
- Streamlit-based user interface
- Chat history management

## Tech Stack

- Python
- LangChain
- FAISS
- LLM APIs
- Streamlit

## How It Works

The application follows a Retrieval-Augmented Generation workflow:

1. Healthcare documents are provided to the system.
2. Documents are processed and converted into embeddings.
3. The embeddings are stored in a FAISS vector database.
4. When a user asks a question, the system performs semantic search.
5. Relevant document information is retrieved.
6. The retrieved context is provided to the language model.
7. The model generates a context-aware response.

## Project Structure

```text
medichat-ai/
│
├── app.py
├── database.py
├── ingest.py
├── medical_pdf/
├── medical_vector_db/
├── pages/
└── README.md
