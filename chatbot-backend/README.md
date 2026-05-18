# Multi-User RAG Chatbot Backend

Production-ready FastAPI backend with authentication, RAG, and streaming.

## Features
- ✅ JWT authentication
- ✅ Per-user document upload (PDF/DOCX/TXT)
- ✅ RAG with FAISS vector search
- ✅ Streaming responses (SSE)
- ✅ Multi-chat support
- ✅ PostgreSQL database

## Setup

### 1. Install dependencies
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up PostgreSQL
```bash
# Using Docker
docker run --name chatbot-db -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:15
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Initialize database
```bash
python -m app.db.init_db
```

### 5. Run server
```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation
Visit http://localhost:8000/docs

## Deployment
See deployment guide in docs/DEPLOY.md
