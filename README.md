# Enterprise AI Platform with Agentic Retrieval

An enterprise-grade, full-stack **Agentic Retrieval-Augmented Generation (RAG)** platform featuring an autonomous **async Python orchestrator**, **Hybrid Retrieval (Dense Qdrant + Sparse BM25 with Reciprocal Rank Fusion)**, **FlashRank Reranking**, **FastAPI SSE Token Streaming**, a pluggable **Knowledge Ingestion Platform**, and a modern **React + TailwindCSS + Vite** ChatGPT-style interface.

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
                  │   Async Agent Orchestrator    │
                  └──────┬─────────────────┬──────┘
                         │                 │
                  [Direct Chat]     [Knowledge / Complex Query]
                         │                 │
                         ▼                 ▼
                   Gemini Direct     Parallel Tool Execution
                                           │
                         ┌─────────────────┼─────────────────┐
                         ▼                 ▼                 ▼
                 Hybrid Retriever     Wikipedia API     Tavily / DuckDuckGo  
                 (Qdrant + BM25)                           Web Search
                         │
                         ▼
                 FlashRank Reranker
```

---

## Key Features

- **Autonomous Agentic Routing**: A custom rule-and-LLM-based routing engine classifies intent, rewrites queries contextually, and executes parallel tool-calling workflows.
- **Hybrid Search & Reranking**: Combines Dense Vector Search (Google Gemini Embeddings + Qdrant) and Sparse Keyword Search (BM25) via Reciprocal Rank Fusion (RRF), enhanced with FlashRank neural reranking.
- **Pluggable Knowledge Ingestion Platform**: A modular ingestion pipeline (`ingestion_platform/`) with clean abstractions for Connectors (PDF, TXT) and Pipeline Stages (Cleaning, Semantic Chunking, Gemini Embedding, Indexing).
- **Real-Time Token Streaming**: Low-latency Server-Sent Events (SSE) stream tokens and reasoning step updates directly to the frontend.
- **Interactive Citations**: Expandable source attribution citations for retrieved documents.
- **Production Ready**: Multi-stage Dockerfiles, `docker-compose.yml`, Google Cloud Run deployment integration, and Google Cloud Build CI/CD automation.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, TailwindCSS v4, Lucide React, React Markdown, Remark GFM |
| **Backend API** | FastAPI, Pydantic v2, Uvicorn, Python 3.12 |
| **AI / Orchestration** | LangChain, Google Gemini (`gemini-3.1-flash-lite`), DuckDuckGo, Tavily API |
| **Search & Indexing** | Qdrant Vector Database, Rank-BM25, PyMuPDF, FlashRank Cross-Encoder |
| **DevOps & CI/CD** | Docker, Docker Compose, Google Cloud Build, Pytest |

---

## Quickstart Guide

### Option 1: Run with Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/sushrutha777/Enterprise-AI-Platform-with-Agentic-Retrieval.git
   cd Enterprise-AI-Platform-with-Agentic-Retrieval
   ```

2. Create a `.env` file in the root directory. Here is a complete template of what you can configure:
   ```env
   # --- Primary AI Model & API Keys ---
   GOOGLE_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_optional
   GROQ_API_KEY=your_groq_api_key_optional
   
   # --- Model Selection ---
   LLM_MODEL=gemini/gemini-3.1-flash-lite
   EMBEDDING_MODEL=models/gemini-embedding-001
   
   # --- AI Gateway Configuration ---
   # Leave blank for Embedded Gateway. Set to URL (e.g. http://localhost:4000) for Standalone Proxy.
   LITELLM_API_BASE=
   
   # --- Vector Database (Qdrant) ---
   VECTOR_DB_TYPE=qdrant
   QDRANT_COLLECTION_NAME=agentic_rag_documents
   QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
   QDRANT_API_KEY=your_qdrant_api_key
   
   # --- Retrieval Tuning ---
   RETRIEVAL_TOP_K=5
   RERANKED_TOP_K=5
   USE_HYBRID_SEARCH=true
   USE_RERANKER=false
   
   # --- Application Environment ---
   ENVIRONMENT=development
   DEBUG=false
   LOG_LEVEL=INFO
   ```

3. Launch all services (starts backend API and frontend):
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

## Knowledge Ingestion Platform

The project includes a robust, independent **Knowledge Ingestion Platform** under [ingestion_platform/](file:///c:/Users/Sushrutha/OneDrive/Desktop/AgenticRAG-with-Web-Search-and-Document-Search/ingestion_platform). This modular platform processes local files and updates the Qdrant vector database.

### Ingestion Pipeline Architecture
- **Connectors**: Extract raw content (e.g., [PDFConnector](file:///c:/Users/Sushrutha/OneDrive/Desktop/AgenticRAG-with-Web-Search-and-Document-Search/ingestion_platform/connectors/pdf.py), [TextConnector](file:///c:/Users/Sushrutha/OneDrive/Desktop/AgenticRAG-with-Web-Search-and-Document-Search/ingestion_platform/connectors/text.py)).
- **Stages**:
  - **DocumentCleaner**: Text sanitization and metadata normalization.
  - **SemanticChunker**: Intelligent chunking of text using semantic boundaries.
  - **GeminiEmbedder**: Generates high-quality vectors using Gemini embeddings.
  - **QdrantIndexer**: Connects to the Qdrant database, manages collections, and uploads vector embeddings.

### How to run ingestion:
You can run the ingestion CLI either via the root helper script or the module directly:

```bash
# Index files from directory (default: ./data)
python ingest.py --source ./data

# Re-index from scratch (drops existing Qdrant collection)
python ingest.py --source ./data --reindex

# Run using the modular CLI entrypoint
python -m ingestion_platform.cli ./data
```

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
- `GET /api/v1/health/ready`: Readiness check for API and LLM configurations.
- `POST /api/v1/voice/transcribe`: Transcribe voice inputs (Speech-to-Text).

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

For complete step-by-step configuration including **Google Cloud Secret Manager** (for securely injecting API keys like `QDRANT_API_KEY`), Cloud Build, and CI/CD automation, see [GCP Deployment Guide](file:///c:/Users/Sushrutha/OneDrive/Desktop/AgenticRAG-with-Web-Search-and-Document-Search/deploy/GCP_DEPLOYMENT.md).

