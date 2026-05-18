from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, chat, files, query

app = FastAPI(
    title="Multi-User RAG Chatbot API",
    version="1.0.0",
    description="Production-ready chatbot with RAG, streaming, and multi-user support"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chats", tags=["chats"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(query.router, prefix="/api/v1/query", tags=["query"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Multi-User RAG Chatbot API", "docs": "/docs"}
