from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    # OpenAI API
    OPENAI_API_KEY: str
    
    # Optional: Authentication (keep for later)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    REDIRECT_URI: Optional[str] = None
    
    # Cohere API (for reranking)
    COHERE_API_KEY: Optional[str] = None
    USE_RERANKING: bool = True
    RERANK_TOP_K: int = 5
    
    # RAG Configuration - OpenAI Models
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_DIMENSIONS: int = 1536
    
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # LLM parameters
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1000
    
    # ChromaDB (Vector Database)
    CHROMA_DATA_PATH: str = "./chroma_data"  # NEW: ChromaDB storage location
    COLLECTION_NAME: str = "knowlia_chunks"   # NEW: Collection name
    
    # App settings
    APP_NAME: str = "Knowlia"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()