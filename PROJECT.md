# Multi-User RAG Chatbot - Complete Documentation

This document contains the complete and cohesive system documentation for the Multi-User RAG Chatbot repository, merging all detailed specifications from the docs/ folder into a single entry point.

## Table of Contents
- [Documentation Hub & Overview](#documentation-hub--overview)
- [System Architecture & Overview](#system-architecture--overview)
- [API Reference & Endpoints](#api-reference--endpoints)
- [RAG Pipeline & Memory Subsystems](#rag-pipeline--memory-subsystems)
- [Agents, Swarm Execution & Prompt System](#agents-swarm-execution--prompt-system)
- [Security Model & Plugin Subsystem](#security-model--plugin-subsystem)
- [Operations, Deployment & Scaling](#operations-deployment--scaling)
- [Error Handling & Reliability Layer](#error-handling--reliability-layer)
- [Development & Contributing Guide](#development--contributing-guide)


---

## Documentation Hub & Overview

Welcome to the central documentation hub for the Multi-User RAG Chatbot. 

## Documentation Index

Below is the directory of all operational and architectural documentation.

1. **[Architecture & System Overview](./ARCHITECTURE.md)**: Deep dive into the DDD architecture, directory structure, data flow, and core design philosophies.
2. **[API Reference](./API_REFERENCE.md)**: Comprehensive breakdown of all FastAPI endpoints, request/response models, and authentication parameters.
3. **[RAG & Memory Systems](./RAG_AND_MEMORY.md)**: Details on the FAISS vector database integration, document parsing, embeddings, chunking, and isolated conversation memory.
4. **[Agents & Tools](./AGENT_AND_TOOLS.md)**: Implementation details of the LLM prompt evolution, execution flow, tool routing (spaces), and swarm logic.
5. **[Plugins & Security](./PLUGINS_AND_SECURITY.md)**: Threat modeling, JWT auth flows, tenant isolation mechanisms, and plugin security routing.
6. **[Operations & Deployment](./OPERATIONS.md)**: Information covering scaling, Vercel/Render deployment, performance tuning, and observability workflows.
7. **[Development & Contributing](./DEVELOPMENT.md)**: Guidelines for local development, branching, testing, and contribution protocols.
8. **[Error Handling & Reliability](./ERROR_HANDLING.md)**: Breakdown of systemic error management, rate limiting, and fallback paradigms.

---
## Quickstart & Installation

### Infrastructure Requirements
- PostgreSQL 14+
- Python 3.10+
- Node.js 18+

### Environment Configuration
Ensure `.env` files are created in both `chatbot-backend` and `chatbot-frontend` directories containing Database URLs, OpenAI Keys, and JWT Secrets as per the `setup-env.sh` spec.

## Core Design Philosophy
The system operates on **strict multi-tenancy at the file and record level**. Every user is isolated via JWT claims, guaranteeing that their vector namespaces (FAISS indexes) and relational data (chat history) are heavily partitioned.


---

## System Architecture & Overview

## System Purpose
The Multi-User RAG Chatbot is designed to provide secure, isolated, and scalable document-augmented LLM chat capabilities for multiple tenants simultaneously. It fuses advanced FAISS vector search with real-time SSE streaming.

## Architectural Layers
```text
      [ End User ]
           | (HTTPS / SSE / Web Speech API)
           v
+--------------------------+
|  Next.js Frontend (UI)   |
|  Tailwind, Auth State    |
+--------------------------+
           | (Axios / Fetch + JWT)
           v
+--------------------------+
|  FastAPI API Gateway     |
|  (Auth, Routers)         |
+--------------------------+
           |
 +---------+---------+
 |                   |
 v                   v
[ Postgres DB ]    [ RAG Pipeline / Services ]
(Users, Chats)     (PDF Parsing, Chunking)
                     |
                     v
             [ FAISS Vector Store ] (Local/Mapped Storage)
                     |
                     v
             [ LLM Engine (OpenAI/Groq) ]
```

## Directory Structure Breakdown
```
chatbot-backend/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ api/          # Route controllers (auth, chat, files, query)
â”‚   â”œâ”€â”€ core/         # Configs (Env, Security JWT tools)
â”‚   â”œâ”€â”€ db/           # Async SQLAlchemy session logic
â”‚   â”œâ”€â”€ models/       # ORM definitions
â”‚   â”œâ”€â”€ schemas/      # Pydantic validation schemas
â”‚   â””â”€â”€ services/     # Core Business logic (rag.py)
â””â”€â”€ uploads/          # Tenant isolated physical files / vector indexes

chatbot-frontend/
â”œâ”€â”€ app/              # Next.js App Router endpoints (chat, auth)
â”œâ”€â”€ components/       # Complex React UI elements (ChatInterface, VoiceInput)
â””â”€â”€ lib/              # Client utilities (api wrapper, auth token mgmt)
```

## Execution Flow (Querying)
1. User submits a prompt (Frontend).
2. Request hits `/api/v1/query/stream` with a valid JWT.
3. `get_current_user` decodes token and extracts `user_id`.
4. System queries PostgreSQL to validate the Chat session.
5. System loads isolated FAISS index from `uploads/{user_id}/faiss_index.bin`.
6. Embeddings generated for the query; FAISS executes Cosine Similarity search.
7. Context chunks compiled into a rigid prompt.
8. OpenAI Async Stream called.
9. FastAPI streams chunks via Server-Sent Events back to Next.js.


---

## API Reference & Endpoints

All endpoints heavily rely on `FastAPI` dependency injection. Unless explicitly stated, endpoints require the `Authorization: Bearer <token>` header, verified via the `get_current_user` dependency.

## Authentication Routes (`/api/v1/auth`)

### `POST /register`
- **Purpose**: Creates a new user.
- **Request Schema**: `UserCreate` (email, password)
- **Response**: User projection (id, email)

### `POST /login`
- **Purpose**: Authenticates user and issues access/refresh tokens.
- **Request Schema**: `UserLogin` or OAuth2 Form Data.
- **Response Schema**: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }`

## Chat Routes (`/api/v1/chat`)

### `POST /`
- **Purpose**: Initialize a new chat thread.
- **Response**: `Chat` ORM serialization (id, user_id, title).

### `GET /`
- **Purpose**: Fetch all chats for the authenticated user.
- **Response**: List of `Chat` objects.

### `GET /{chat_id}/messages`
- **Purpose**: Retrieve historical interaction for a thread. Strict `user_id` validation applies.

## File Routes (`/api/v1/files`)

### `POST /upload`
- **Purpose**: Multi-part form upload for RAG parsing.
- **Process**: File is saved to `uploads/{user_id}/`, parsed by `pdfplumber`/`python-docx`, chunked, embedded, and mapped into FAISS.
- **Security**: Validates against MIME types and executes path traversal sanitization.

## Query Routes (`/api/v1/query`)

### `POST /`
- **Purpose**: Non-streaming RAG inference.
- **Request Schema**: `QueryRequest` (chat_id, query)

### `GET /stream`
- **Purpose**: Primary interface for real-time inference.
- **Process**: Returns `StreamingResponse` (SSE) yielding `event: message\ndata: {token}\n\n`.


---

## RAG Pipeline & Memory Subsystems

## RAG Ingestion Pipeline
Centralized in `app/services/rag.py`.

### 1. Document Extraction
- **PDF**: Parsed linearly via `pdfplumber` keeping metadata roughly linked to pages.
- **DOCX**: Iterated via `python-docx` by paragraphs.
- **TXT**: Read via raw UTF-8 parsing.

### 2. Document Chunking
Text logic is split to optimize dense retrieval.
- **Strategy**: Sliding window chunking.
- **Chunk Size**: 800 tokens targeting optimal LLM context ingestion.
- **Overlap**: 100 tokens to prevent contextual clipping on hard borders.

### 3. Embedding Generation
Leverages `sentence-transformers` locally (e.g., `all-MiniLM-L6-v2`) or OpenAI embeddings depending on the active space/configuration. Transforms strings into dense matrices.

---

## Vector Database (FAISS)
Instead of a centralized Vector DB, we employ **per-user inverted indexes** utilizing FAISS.
- **Storage**: `uploads/{user_id}/faiss_index.bin`.
- **Scaling considerations**: Operates extremely efficiently for individual limits, isolating noise vectors from other users.
- **Failure modes**: Memory scaling is bounded by disk I/O; heavily utilized instances load FAISS indexes into an LRU Cache.

## Conversation & Knowledge Memory
### Relational Memory
Chat history is permanently persisted in PostgreSQL under the `messages` table mapped by `chat_id`. 
During standard querying, the `chat.py` interface rebuilds conversational graphs up to a specific limit (e.g., last 10 messages) to ground the model context without saturating the context window.

### Metadata Linking (Grounding)
When FAISS returns matching chunks, it bridges back to `metadata.json` ensuring exact File ID and Page references are cited in the API response payload.


---

## Agents, Swarm Execution & Prompt System

While this application operates primarily as a conversational RAG platform rather than a pure autonomous background agent, its LLM synthesis pipeline utilizes agentic reasoning flows.

## Prompt Evolution and Routing
The core LLM prompt resides dynamically within `build_rag_context()`.

```text
User Query 
   |
[ Tool Router / Intent Classifier ] (Optional Space Override)
   |
   +--> Path A: Chitchat (No Vector Lookup)
   +--> Path B: Deep Document Retrieval <-- (Standard Flow)
```

1. **System Prompt**: Enforces boundaries. It strictly instructs the agent to rely *exclusively* on the provided context vectors. If the answer does not exist within the chunks, the agent is directed to politely refuse.
2. **Context Padding**: Up to Top-K (commonly 5) vectors are appended as raw strings into an `<Information>` block.
3. **Conversational Drift**: The latest PostgreSQL historical messages are prepended to ensure anaphoric resolution (e.g., "What does it mean on page 4?").

## Model Override / Spaces Architecture
The `stream_rag_query` accepts space/model overrides. This acts as a rudimentary *Swarm Router*. Different spaces can route the user query to different provider tiers.
- High complexity code reasoning â†’ Routed to `gpt-4o`.
- General query / draft summarization â†’ Routed to `gpt-4o-mini` or Groq endpoints.

## Tool Execution
Future plugins expand the `services/` directory allowing the Assistant to format JSON outputs to trigger subsequent microservices before yielding the final tokenized text stream to the user.


---

## Security Model & Plugin Subsystem

## Core Architectural Security
This repository is built defensively for a multi-tenant environment. Data leakage is mathematically impossible at the vector level unless the directory `user_id` mapping is compromised.

1. **Authentication Boundaries**
   - JWT tokens are validated intrinsically on *every* request requiring state. 
   - Refresh Token cycling ensures short-lived Access Tokens (e.g., 30 minutes).
2. **Path Traversal Defenses**
   - File uploads are strictly sanitized. `secure_filename()` ensures arbitrary executable payloads cannot break out of `/uploads/{user_id}/`.
3. **MIME Type Assertions**
   - RAG parsing explicitly blocks non-permitted file extensions, protecting the parsers (`pdfplumber` / `python-docx`) from zero-day exploit variants embedded in malformed PDFs.

## Plugin / Extendable Subsystems
The RAG processing is modular. Adding a new file-type processor (e.g., `.xlsx`) acts as a "Plugin".
- **Discovery**: Registered in `services/rag.py` under the parser mapping switch.
- **Execution**: Runs synchronously during upload.
- **Sandboxing**: Extraction processing operates linearly; high-availability configurations execute parsers on isolated queue workers (e.g., Celery) to prevent CPU hogging.

## Rate Limiting & DoS
- FastAPI integration (via Starlette middlewares) throttles aggressive query bursts.
- LLM API calls are rate-limited per tenant to prevent runaway cost accumulation to external providers like OpenAI.


---

## Operations, Deployment & Scaling

## Deployment Infrastructure
The system follows a split-tier deployment model optimally suited for PaaS pipelines.

### Staging & Local
`docker-compose.yml` mounts local volumes and manages local PostgreSQL ports. Best for rapid iteration.

### Production
- **Frontend**: Shipped to **Vercel**. Provides CDN Edge caching, Automatic Next.js API route compilation, and zero-downtime CI/CD.
- **Backend**: Deployed to **Render** or **Railway**. Utilizes Dockerfile encapsulation for Python 3.10 environments.
- **Database**: Managed Neon Serverless PostgreSQL or Render Managed PG.

## Scalability & Performance
### Horizontal Scaling
- **API Nodes:** FastAPI/Uvicorn scales horizontally by increasing worker processes (`--workers 4`). Because sessions are stateless (JWT), requests can be load-balanced in an active/active setup.
- **PostgreSQL Connection Limits:** `AsyncSession` combined with `SQLAlchemy` connection pooling guarantees we do not exhaust the PG instance limit (usually ~100 max connections).
- **Vector DB Scale:** Since FAISS sits in isolated files, volume access needs High-IOPS networked attached storage across backend nodes.

### Performance & Caching
- **LRU Vectors**: Disk reads for `.bin` files run in the 10-50ms range. 
- Next.js fetches are cached aggressively except for the dynamic `/api/query` streaming routes.

## Observability & Telemetry
1. **Application Logging**: Python's native `logging` framework tracks failed FAISS loads, slow parsing execution times, and HTTP errors.
2. **Bash Telemetry**: Utilizing `view-logs.sh` and `health-check.sh` allows rapid DevOps introspection directly onto the VMs.


---

## Error Handling & Reliability Layer

## Systemic Failure Modes
This environment relies on continuous uptime. All system pathways are trapped by global exception handlers to prevent internal stack traces leaking to API consumers.

### 1. File Upload Processing Failures
- **Scenario:** Corrupted PDF attempting to parse.
- **Handling:** `pdfplumber` exception is caught. HTTP 422 Unprocessable Entity thrown gracefully denoting "Unreadable file format".
- **Rollback:** Transaction commits are suspended. Stray partial files on disk are unlinked/deleted by the `finally` block to protect storage volume sizing.

### 2. FAISS Index Out-of-Sync
- **Scenario:** Database record exists for file_id, but `.bin` chunk index missing on disk.
- **Handling:** Fallback to safe mode -> RAG Context returns empty, LLM gracefully acknowledges a lack of context rather than crashing the SSE stream. Error logged for admin alerting.

### 3. OpenAI Connectivity Drops
- **Scenario:** Rate limiting (429) or OpenAI 500 errors mid-stream.
- **Handling:** SSE stream yields an explicit error JSON token payload indicating provider disruption, frontend handles event catching and presents toast notification.

## Database Consistency
- `AsyncSession` explicitly opens on HTTP Request start and closes upon completion.
- Transactions are utilized during multi-table writes (e.g., creating a file metadata record alongside FAISS building) so that a failure in Vector generation prevents orphaned Database records.


---

## Development & Contributing Guide

## Setting up for Local Development
We encourage developers to utilize isolated environments.

1. Init Postgres: `docker-compose up -d postgres`
2. Backend: `source setup-env.sh`, establish `.env`, and boot Uvicorn.
3. Frontend: `npm install && npm run dev`.

## Code Walkthrough & Understanding Architecture
- Start in `main.py` -> See the FastAPI router injection.
- Navigate to `api/v1/auth.py` -> See JWT flow.
- Investigate `services/rag.py` -> This is the most complex component containing all extraction, windowing/chunking mathematics, and FAISS orchestration.
- Trace Next.js React Trees in `chatbot-frontend/app/chat/page.tsx` and identify the SSE hook in `components/ChatInterface.tsx`.

## Extending System
### Adding New Agents/Tools
To add a new tool or execution space:
1. Register tool schema in `schemas/`.
2. Register override route logic in `api/v1/query.py`.
3. Scaffold function in `services/`.
4. Ensure dependency injection explicitly passes the AsyncSession.

### Adding New Extractors
To implement `.csv` support:
1. Add `pandas` to `requirements.txt`.
2. Create mapping logic inside `extract_text_from_file()`.
3. Write chunking strategy optimized for tabular layout.

## Contribution Workflow
- **Branching**: `feature/your-impl` or `fix/issue-id`.
- **Committing**: Adhere to semantic commit guidelines.
- **Testing**: Run pytest locally. Ensure database mocks tear down correctly post-suite. 
- **PRs**: Require one approving engineer. CI will statically type check `Next.js` and enforce PEP8 linting for Python.
