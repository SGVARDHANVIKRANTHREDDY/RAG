from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, BaseModel
from typing import List, Dict, Optional
import os

class SpaceConfig(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    provider: str  # e.g. "openai"
    default_model: str
    use_rag: bool

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Chatbot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "dev-secret-change-this-in-production-min-32chars!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"

    CORS_ORIGINS: str = "http://localhost:3000"

    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1000

    SPACES: Dict[str, SpaceConfig] = {
        "general": SpaceConfig(
            id="general",
            name="General Assistant",
            description="General-purpose AI assistant using your documents when available.",
            provider="openai",
            default_model="gpt-4o-mini",
            use_rag=True,
            system_prompt="You are a helpful assistant. Use context if provided, but indicate when you are not sure.",
        ),
        "coding": SpaceConfig(
            id="coding",
            name="Coding Assistant",
            description="Programming-focused assistant with code examples and debugging help.",
            provider="openai",
            default_model="gpt-4o-mini",
            use_rag=True,
            system_prompt="You are an expert coder. Treat document context as project-specific documentation.",
        ),
        "docs_only": SpaceConfig(
            id="docs_only",
            name="Docs-Only QA",
            description="Strictly answers from documents only.",
            provider="openai",
            default_model="gpt-4o-mini",
            use_rag=True,
            system_prompt="You are a strict QA bot. Only answer using the exact information in the documents provided.",
        ),
        "chatgpt": SpaceConfig(
            id="chatgpt",
            name="ChatGPT-like",
            description="Standard chatbot, ignores all documents.",
            provider="openai",
            default_model="gpt-4o-mini",
            use_rag=False,
            system_prompt="You are a helpful general assistant. Ignore any rag context.",
        ),
        "summarizer": SpaceConfig(
            id="summarizer",
            name="Summarizer",
            description="Summarizes lengths documents.",
            provider="openai",
            default_model="gpt-4o-mini",
            use_rag=True,
            system_prompt="You are a summarization expert. Outline and summarize the main points in the provided context.",
        ),
    }

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    TOP_K_RETRIEVAL: int = 5

    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt", ".md"]
    UPLOAD_DIR: str = "uploads"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="",
    )


settings = Settings()

def get_space(space_id: Optional[str]) -> SpaceConfig:
    if space_id and space_id in settings.SPACES:
        return settings.SPACES[space_id]
    return settings.SPACES["general"]
