# Enterprise AI Platform with Agentic Retrieval

An enterprise-grade, full-stack **Agentic Retrieval-Augmented Generation (RAG)** platform featuring an autonomous **LangGraph** reasoning engine, **Hybrid Retrieval (Dense FAISS + Sparse BM25 with Reciprocal Rank Fusion)**, **FlashRank Reranking**, **FastAPI SSE Token Streaming**, and a modern **React + TailwindCSS + Vite** ChatGPT-style interface.

---

## System Architecture

```text
                  ┌───────────────────────────────┐
                  │    React + Vite Frontend      │
                  │  (Tailwind, SSE, Dark Theme)  │
                  └──────────────┬────────────────┘
                                 │ REST / SSE
                                 ▼
                  ┌───────────────────────────────┐
                  │       FastAPI Backend         │
                  │   (Auth, Streaming, Services) │
                  └──────────────┬────────────────┘
                                 │
                  ┌──────────────▼────────────────┐
                  │    LangGraph StateGraph       │
                  └──────┬─────────────────┬──────┘
                         │                 │
              [Direct Chat]                [Knowledge / Complex Query]
                         │                 │
                         ▼                 ▼
                 Gemini Direct      ReAct Reasoning Agent
                                           │
                         ┌─────────────────┼─────────────────┐
                         ▼                 ▼                 ▼
                 Hybrid Retriever     Wikipedia API    Tavily Web Search
                 (FAISS + BM25)
                         │
                         ▼
                 FlashRank Reranker
```

---

## Key Features

- **Autonomous Agentic Routing**: LangGraph orchestrates query classification, contextual query rewriting, and autonomous tool calling.
- **Hybrid Search & Reranking**: Combines Dense Vector Search (Google Gemini Embeddings + FAISS) and Sparse Keyword Search (BM25) via Reciprocal Rank Fusion (RRF), enhanced with FlashRank neural reranking.
- **Real-Time Token Streaming**: Low-latency Server-Sent Events (SSE) stream tokens and reasoning step updates directly to the frontend.
- **Persistent Multi-Session History**: Conversation management with SQLite / PostgreSQL backend via SQLAlchemy and JWT authentication.
- **Multi-Source Knowledge Ingestion**: Supports local documents (PDF, TXT, DOCX, Markdown) and direct Website URL crawling.
- **Interactive Citations & Feedback**: Expandable source attribution citations and user feedback ratings (thumbs up/down).
- **Production Ready**: Multi-stage Dockerfiles, `docker-compose.yml`, and GitHub Actions CI/CD workflows.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, TailwindCSS v4, Lucide React, React Markdown, Remark GFM |
| **Backend API** | FastAPI, Pydantic v2, SQLAlchemy, Uvicorn, Python 3.12 |
| **AI / Orchestration** | LangGraph, LangChain, Google Gemini (`gemini-flash-latest`), Tavily API |
| **Search & Indexing** | FAISS, Rank-BM25, PyMuPDF, FlashRank Cross-Encoder |
| **DevOps & CI/CD** | Docker, Docker Compose, GitHub Actions, Pytest |

---

## Quickstart Guide

### Option 1: Run with Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/sushrutha777/Enterprise-AI-Platform-with-Agentic-Retrieval.git
   cd Enterprise-AI-Platform-with-Agentic-Retrieval
   ```

2. Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_optional
   JWT_SECRET=your_secret_key
   ```

3. Launch all services:
   ```bash
   docker-compose up --build
   ```
   - **Frontend UI**: [http://localhost:3000](http://localhost:3000)
   - **Backend API & Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Local Development

#### 1. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI Server
python -m uvicorn app.main:app --port 8000 --reload
```

#### 2. Frontend Setup

```bash
cd frontend

# Install node dependencies
npm install

# Start Vite dev server
npm run dev
```

The application will be live at `http://localhost:5173`.

---

## Running Tests

```bash
# Run pytest suite
pytest tests/ -v
```

---

## API Documentation

Once the backend is running, explore interactive Swagger API docs at `http://127.0.0.1:8000/docs`:

- `POST /api/v1/chat/stream`: SSE Streaming endpoint for LangGraph RAG.
- `GET /api/v1/conversations`: List and manage chat sessions.
- `POST /api/v1/documents/upload`: Ingest and index PDF/TXT/DOCX documents.
- `POST /api/v1/documents/upload-url`: Ingest and index website URLs.
- `POST /api/v1/auth/register` & `POST /api/v1/auth/login`: JWT user authentication.
- `POST /api/v1/feedback`: Submit user ratings for model responses.

---

## Google Cloud Platform (GCP) Deployment

The application is containerized and ready for deployment to **Google Cloud Run**:

```powershell
# Windows PowerShell
.\deploy\deploy-gcp.ps1
```

```bash
# Linux / macOS / Cloud Shell
./deploy/deploy-gcp.sh
```

For complete step-by-step configuration including Secret Manager, Cloud Build, and CI/CD automation, see [GCP Deployment Guide](file:///deploy/GCP_DEPLOYMENT.md).

