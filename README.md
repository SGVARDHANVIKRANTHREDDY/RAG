# Multi-User RAG Chatbot Project

Complete production-ready chatbot with:
- ✅ Multi-user authentication (JWT)
- ✅ RAG document chat (PDF/DOCX/TXT)
- ✅ Streaming responses
- ✅ Voice input/output
- ✅ Dark mode
- ✅ Chat history

## Project Structure

```
chatbot-backend/     # FastAPI backend
chatbot-frontend/    # Next.js frontend
```

## Quick Start

### Backend Setup
```bash
cd chatbot-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd chatbot-frontend
npm install
npm run dev
```

## API Documentation
http://localhost:8000/docs
