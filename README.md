# Enterprise AI Platform with Agentic Retrieval

An enterprise-grade, full-stack **Agentic Retrieval-Augmented Generation (RAG)** platform featuring an autonomous **async Python orchestrator**, **Hybrid Retrieval (Dense Qdrant + Sparse BM25 with Reciprocal Rank Fusion)**, **FlashRank Reranking**, **FastAPI SSE Token Streaming**, a pluggable **Knowledge Ingestion Platform**, and a modern **React + TailwindCSS + Vite** ChatGPT-style interface.

> [!NOTE]
> ### Current LLM Setup (Out of the Box)
> - **Primary LLM**: **Google Gemini 3.1 Flash Lite** (`gemini/gemini-3.1-flash-lite`)
> - **Automated Fallback**: **Groq Llama 3** (`groq/llama3-8b-8192` / `llama-3.3-70b`) for zero-downtime failover
> - **Embeddings**: **Google Gemini Embeddings** (`models/gemini-embedding-001`)
> - **Future-Proof**: Ready to switch to **Anthropic Claude 3.5** or **OpenAI GPT-4o** via LiteLLM with zero code changes.

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
            ┌────────────────────────────┘                 └────────────────────────────┐
            ▼                                                                           ▼
   [ Direct Conversation ]                                                   [ Knowledge / Agentic Query ]
            │                                                                           │
            ▼                                                                           ▼
┌───────────────────────────────┐                                       ┌───────────────────────────────┐
│        LLM Direct Chat        │                                       │    Parallel Tool Execution    │
│  - Primary: Google Gemini     │                                       └───────────────┬───────────────┘
│  - Fallback: Groq Llama 3     │                                                       │
└───────────────────────────────┘                                    ┌──────────────────┼──────────────────┐
                                                                     ▼                  ▼                  ▼
                                                            ┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐
                                                            │  Hybrid Search  │ │ Wikipedia API │ │ Tavily / DDG    │
                                                            │ (Qdrant + BM25) │ └───────────────┘ │ Web Search      │
                                                            └────────┬────────┘                   └─────────────────┘
                                                                     │
                                                                     ▼
                                                            ┌─────────────────┐
                                                            │ FlashRank       │
                                                            │ Neural Reranker │
                                                            └─────────────────┘
```

---

## Key Features

- **Dual-Provider Resilience (Gemini + Groq Fallback)**: Runs **Google Gemini 3.1 Flash Lite** as primary generation engine with automatic, sub-second fallback to **Groq Llama 3** if Google rate-limits or fails.
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
| **Active LLM Engine** | **Primary**: Google Gemini (`gemini-3.1-flash-lite`)<br>**Fallback**: Groq (`llama3-8b` / `llama-3.3-70b`)<br>**Gateway**: LiteLLM |
| **Search & Indexing** | Qdrant Vector Database, Gemini Embeddings, Rank-BM25, PyMuPDF, FlashRank Cross-Encoder |
| **Web Search Tools** | Tavily Search API, DuckDuckGo Search, Wikipedia API |
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
    # Primary AI Model and API Keys
    GOOGLE_API_KEY=your_gemini_api_key_here
    OPENAI_API_KEY=your_openai_api_key_optional
    ANTHROPIC_API_KEY=your_anthropic_api_key_optional
    TAVILY_API_KEY=your_tavily_api_key_optional
    GROQ_API_KEY=your_groq_api_key_optional
    
    # Model Selection
    LLM_MODEL=gemini/gemini-3.1-flash-lite
    EMBEDDING_MODEL=models/gemini-embedding-001
    
    # AI Gateway Configuration
    # [CURRENT STATE]: Leave blank. The app uses an Embedded Gateway to handle Gemini -> Groq fallbacks internally.
    # [FUTURE SCOPE]: Set to a URL (e.g. 'http://localhost:4000') if you deploy a standalone LiteLLM Proxy Server in the future to handle team budgets, API key load balancing, and strict cost tracking.
    LITELLM_API_BASE=
    
    # Vector Database (Qdrant) Configuration
    VECTOR_DB_TYPE=qdrant
    QDRANT_COLLECTION_NAME=agentic_rag_documents
    QDRANT_URL=https://your-cluster-id.cloud.qdrant.io
    QDRANT_API_KEY=your_qdrant_api_key
    
    # Retrieval Tuning Settings
    RETRIEVAL_TOP_K=5
    RERANKED_TOP_K=5
    USE_HYBRID_SEARCH=true
    USE_RERANKER=true
    
    # Application Environment
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

## Multi-LLM Provider Switching & AI Gateway Architecture

The platform is designed with a two-phase AI Gateway strategy powered by **LiteLLM**, allowing seamless transitions between model providers (**Google Gemini**, **OpenAI**, **Anthropic Claude**, **Groq**, **AWS Bedrock**) without touching agent business logic.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             AI GATEWAY MODES                                │
│                                                                             │
│  [CURRENT STATE] Embedded In-Process Gateway                                │
│  FastAPI Backend ──(In-Process LiteLLM SDK)──► Gemini / Fallback Groq       │
│                                                                             │
│  [FUTURE SCOPE] Standalone LiteLLM Proxy (When Application Scales)          │
│  FastAPI Backend ──(LITELLM_API_BASE:4000)──► Central AI Gateway Proxy      │
│                                                  │                          │
│                    ┌─────────────────────────────┼─────────────────┐        │
│                    ▼                             ▼                 ▼        │
│              Anthropic Claude              OpenAI GPT-4o     Google / Groq  |
│              (Team A Quota)               (Team B Quota)    (Auto-Fallback) |
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1. Current State: Embedded In-Process Gateway (Active by Default)

> **Active Configuration**:
> - **Primary LLM**: `gemini/gemini-3.1-flash-lite` (via `GOOGLE_API_KEY`)
> - **Automatic Fallback**: `groq/llama-3.3-70b-versatile` or `groq/llama3-8b-8192` (via `GROQ_API_KEY`)
> - **Vector Embeddings**: `models/gemini-embedding-001`

* **How it Works**: The backend uses the embedded Python `litellm` library directly inside [app/llm/gateway.py](file:///c:/Users/Sushrutha/OneDrive/Desktop/AgenticRAG-with-Web-Search-and-Document-Search/app/llm/gateway.py).
* **Zero Infrastructure Overhead**: Runs within the FastAPI process with no extra proxy containers or network hops.
* **Instant Fallback**: If Gemini encounters rate limits (HTTP 429) or temporary outages, LiteLLM automatically shifts to Groq within milliseconds without dropping the user's stream.
* **Switching Models**: Swap models anytime by updating `.env`:

| Provider | Model String (`LLM_MODEL`) | Required API Key in `.env` | Status |
| :--- | :--- | :--- | :--- |
| **Google Gemini** | `gemini/gemini-3.1-flash-lite` | `GOOGLE_API_KEY` | **Active Primary** |
| **Groq Llama** | `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` | **Active Fallback** |
| **OpenAI** | `gpt-4o` or `gpt-4o-mini` | `OPENAI_API_KEY` | Optional Drop-in |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` | Optional Drop-in |
| **AWS Bedrock** | `bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0` | AWS Credentials | Optional Drop-in |

---

### 2. Future Scope: Standalone LiteLLM Proxy Server (When the Application Scales)

As traffic grows across multiple enterprise teams, departments, or microservices, you can deploy a standalone **LiteLLM Proxy Server** (`ghcr.io/berriai/litellm:main-latest`) to act as a centralized enterprise AI control plane.

#### Why Scale to a Standalone Proxy?
* **Centralized Budget & Cost Management**: Allocate virtual API keys with strict monthly spend limits per department or team.
* **Unified Key Rotation & Governance**: Store enterprise provider API keys in one central gateway rather than distributing them across multiple apps.
* **Zero-Downtime Model Swapping**: Shift traffic from Claude to OpenAI or Gemini globally without modifying or redeploying any application code.
* **Admin Analytics Dashboard**: Web console at `http://localhost:4000/ui` showing real-time token spend, latency graphs (p50/p99), and error rates.
* **Standardized Endpoints**: Exposes 100% OpenAI-compatible `/v1/chat/completions`, `/v1/embeddings`, and `/v1/models` endpoints.

#### Step 1: Create `litellm-config.yaml`
```yaml
model_list:
  # Primary Enterprise Model (Claude 3.5 Sonnet)
  - model_name: enterprise-chat
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: "os.environ/ANTHROPIC_API_KEY"

  # Secondary Fallback Model (OpenAI GPT-4o-mini)
  - model_name: gpt-4o-mini
    litellm_params:
      model: gpt-4o-mini
      api_key: "os.environ/OPENAI_API_KEY"

  # Fast Open-Source Fallback (Groq)
  - model_name: groq-llama
    litellm_params:
      model: groq/llama-3.3-70b-versatile
      api_key: "os.environ/GROQ_API_KEY"

litellm_settings:
  fallbacks: [{"enterprise-chat": ["gpt-4o-mini", "groq-llama"]}]
  num_retries: 3
  request_timeout: 30
```

#### Step 2: Run the Proxy Container
```bash
docker run -d \
  --name litellm-proxy \
  -p 4000:4000 \
  -v $(pwd)/litellm-config.yaml:/app/config.yaml \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e OPENAI_API_KEY="sk-..." \
  -e GEMINI_API_KEY="AIzaSy..." \
  -e GROQ_API_KEY="gsk_..." \
  -e LITELLM_MASTER_KEY="sk-master-admin-key" \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml --port 4000
```

#### Step 3: Connect this Application to the Proxy
In your `.env`:
```dotenv
# Point backend to the LiteLLM Proxy endpoint
LITELLM_API_BASE=http://localhost:4000

# Use the model alias registered in the proxy configuration
LLM_MODEL=enterprise-chat
```

---

## Running Tests & Evaluation
 
### 1. PyTest Unit Tests
```bash
pytest tests/ -v
```

### 2. RAGAS Automated Evaluation Benchmark
Evaluate Faithfulness, Answer Relevancy, Context Precision, and Context Recall using RAGAS:

```bash
# Run automated benchmark
python eval/evaluate_ragas.py
```

Results are scored from `0.0` to `1.0` and saved automatically to `eval/ragas_report.json`.

---

## Production Observability & Tracing (LangSmith)

The platform supports native integration with **LangSmith** for real-time visual execution tracing, latency breakdown per token, tool call tracking, and user feedback:

1. Obtain a free API key from [smith.langchain.com](https://smith.langchain.com).
2. Add your key to `.env`:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_free_key_here
LANGCHAIN_PROJECT=Enterprise-Agentic-RAG
```
3. All streaming chat interactions and tool calls will now automatically record live traces into your LangSmith dashboard.

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

