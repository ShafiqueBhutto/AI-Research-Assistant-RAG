# 🤖 AI Research Assistant — RAG-Based Document Question Answering System

An AI-powered Research Assistant that allows users to upload PDF documents and ask questions about their content.

The system uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and generate grounded answers using an LLM, along with source references.

---

## 📌 Overview

The AI Research Assistant is a production-style document question-answering application designed to demonstrate an end-to-end **RAG pipeline**.

Users can:

- Upload PDF documents
- Process and chunk document text
- Generate vector embeddings
- Store embeddings in ChromaDB
- Ask questions about uploaded documents
- Retrieve the most relevant document chunks
- Generate answers using Google's Gemini LLM
- View source documents and page references
- Continue multi-question conversations
- Access previous chat sessions
- Select and manage uploaded documents

The goal of this project is to build a practical AI Engineering application using modern backend, database, vector search, and LLM technologies.

## 🎥 Demo

See the AI Research Assistant in action:

[▶️ Watch Demo Video](https://youtu.be/VT-teV_7XqI)

## 🖥️ Screenshots

### Document Upload & Management

![Document Upload](assets/screenshots/document-upload.png)

### AI-Powered Question Answering

![AI Answer](assets/screenshots/chat-response.png)

### Chat History & Document Selection

![Chat History](assets/screenshots/dashboard.png)

---

## ✨ Features

### 📄 PDF Document Processing

- Upload PDF documents through the Streamlit interface
- Extract text from PDF files using PyMuPDF
- Split documents into smaller chunks
- Store document metadata in PostgreSQL

### 🧠 Embeddings

- Generate semantic embeddings for document chunks
- Use `sentence-transformers` for embedding generation
- Store embeddings in ChromaDB for efficient similarity search

### 🔎 Semantic Search

When a user asks a question:

1. The question is converted into an embedding
2. ChromaDB performs similarity search
3. The most relevant document chunks are retrieved
4. Retrieved chunks are passed to the LLM as context

### 🤖 AI-Powered Answers

The application uses **Google Gemini** to generate answers based only on the retrieved document context.

The system is instructed to:

- Avoid using outside knowledge
- Avoid making up information
- Answer using retrieved document content
- Clearly state when the answer cannot be found

### 💬 Conversational Chat

Users can ask multiple questions about the same document within a chat session.

Chat sessions and messages are stored in PostgreSQL.

### 📚 Source References

Each answer can include source information such as:

- Document filename
- Page number
- Document ID
- Retrieval distance

This makes the generated answers more traceable and transparent.

### 🗂️ Previous Chat Sessions

Previous conversations are stored and can be reopened from the sidebar.

The application restores:

- Previous questions
- Previous answers
- Source references
- Associated document

### 📑 Document Management

Users can:

- Upload documents
- Select existing documents
- View stored chunk counts
- Delete documents

Deleting a document also removes its associated vector chunks.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       User          │
                    │                     │
                    │ Upload PDF / Ask    │
                    │      Question       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │     Frontend        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐        ┌──────────────────┐
       │  PDF Processing  │        │    PostgreSQL    │
       │    & Chunking    │        │                  │
       └────────┬─────────┘        │ Documents        │
                │                  │ Chat Sessions    │
                ▼                  │ Chat Messages    │
       ┌──────────────────┐        └──────────────────┘
       │    Embeddings    │
       │ Sentence         │
       │ Transformers     │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │     ChromaDB     │
       │  Vector Database │
       └────────┬─────────┘
                │
          Similarity Search
                │
                ▼
       ┌──────────────────┐
       │   Retrieved      │
       │ Document Chunks  │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │   Gemini LLM     │
       │ Answer Generation│
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │ Answer + Sources │
       └────────┬─────────┘
                │
                ▼
       ┌──────────────────┐
       │    Streamlit     │
       │    Interface     │
       └──────────────────┘

       🔄 RAG Pipeline

The application follows the following RAG workflow:

PDF Upload
    ↓
Text Extraction
    ↓
Document Chunking
    ↓
Embedding Generation
    ↓
Vector Storage in ChromaDB
    ↓
User Question
    ↓
Question Embedding
    ↓
Similarity Search
    ↓
Relevant Chunks Retrieved
    ↓
Context Construction
    ↓
Gemini LLM
    ↓
Grounded Answer
    ↓
Source References


🛠️ Tech Stack
Backend
Python
FastAPI
Uvicorn
Pydantic
Frontend
Streamlit
AI / Machine Learning
Sentence Transformers
Google Gemini
NumPy
Scikit-learn
Vector Database
ChromaDB
Database
PostgreSQL
SQLAlchemy
Psycopg2
Document Processing
PyMuPDF
Development Tools
Git
GitHub
Python Virtual Environment


📁 Project Structure
AI-Research-Assistant-RAG/
│
├── app/
│   ├── api/
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── models/
│   ├── rag/
│   │   ├── embeddings.py
│   │   ├── chunking.py
│   │   └── vector_store.py
│   │
│   ├── schemas/
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   └── llm_service.py
│   │
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── data/
│   ├── chroma/
│   └── uploads/
│
├── tests/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt


⚙️ Installation
1. Clone the repository
git clone https://github.com/ShafiqueBhutto/AI-Research-Assistant-RAG.git
cd AI-Research-Assistant-RAG
2. Create a virtual environment

Windows:

python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt


🔐 Environment Variables
Create a .env file in the project root.

Use .env.example as a template.

DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/ai_research_assistant

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
Important

Never commit your .env file or API keys to GitHub.



🗄️ PostgreSQL Setup
Create a PostgreSQL database named:

ai_research_assistant

Then configure the database connection in .env.

The application uses PostgreSQL to store:

Document metadata
Chat sessions
Chat messages
Source references


▶️ Running the Application
Start FastAPI

From the project root:

uvicorn app.main:app --reload

The API will run at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Start Streamlit

Open another terminal and activate the virtual environment.

Then run:

streamlit run frontend/app.py

The Streamlit application will open at:

http://localhost:8501
📸 Screenshots
Main Application

Add your main application screenshot here.

screenshots/main-ui.png
Document Upload

Add your document upload screenshot here.

screenshots/document-upload.png
AI Response & Sources

Add your AI response screenshot here.

screenshots/chat-response.png

Replace the filenames above with your actual screenshot filenames after adding them to the repository.

🎥 Demo

A complete demonstration of the AI Research Assistant is available below.

Demo workflow:
Upload a research paper
Process the PDF
Ask questions about the document
Retrieve relevant information
Generate an AI-powered answer
Display source references
Continue the conversation
Reopen previous chat sessions

Add your demo video or GitHub video link here.



🧪 Example Questions
After uploading a research paper, users can ask questions such as:

What is the main objective of this paper?
What are the main challenges discussed in the paper?
What methodology does the paper propose?
What are the key findings of the research?
What limitations are mentioned by the authors?

The system retrieves relevant document chunks and generates an answer based on the retrieved context.

🧠 How RAG Works in This Project
Traditional LLM applications may rely only on the knowledge contained within the language model.
This project uses Retrieval-Augmented Generation (RAG) to provide document-specific answers.
The process is:

1. Retrieve
Relevant chunks are retrieved from ChromaDB using semantic similarity search.

2. Augment
The retrieved chunks are combined into a context provided to the LLM.

3. Generate
Gemini generates the final answer using the retrieved context.
This approach helps the application provide answers grounded in the uploaded documents.



🔒 Data & Security
Sensitive configuration values are stored in environment variables.
The following files/directories are excluded from Git:

.env
data/uploads/
data/chroma/
*.sql
.venv/
__pycache__/

API keys and database credentials should never be committed to the repository.

🚀 Future Improvements
Possible future improvements include:

User authentication and authorization
Streaming AI responses
Improved conversation memory
Multi-document question answering
Re-ranking retrieved chunks
Hybrid search
Better citation formatting
OCR support for scanned PDFs
Cloud deployment
Docker containerization
Automated testing and CI/CD
Production monitoring and logging



🎯 Project Objective
This project was built to demonstrate practical skills in:
AI Engineering
Retrieval-Augmented Generation
Large Language Models
Vector Databases
Semantic Search
Backend API Development
Database Design
Document Processing
AI Application Development

It combines these technologies into an end-to-end AI application rather than demonstrating them as isolated experiments.

👨‍💻 Author
Shafique Bhutto
Computer Science Graduate
Sukkur IBA University