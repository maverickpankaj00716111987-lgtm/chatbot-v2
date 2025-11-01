from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    database_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    
    primary_model: str = Field(default="gpt-4-turbo-preview")
    fallback_model: str = Field(default="claude-3-sonnet-20240229")
    embedding_model: str = Field(default="text-embedding-3-small")
    
    primary_model_provider: str = Field(default="openai")
    fallback_model_provider: str = Field(default="anthropic")
    
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    langsmith_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("LANGSMITH_API_KEY"))
    langsmith_project: str = Field(default="rag-chatbot")
    
    max_tokens: int = Field(default=2000)
    temperature: float = Field(default=0.7)
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    top_k_docs: int = Field(default=5)
    
    short_term_memory_window: int = Field(default=5)
    max_retry_attempts: int = Field(default=3)
    retry_delay: float = Field(default=1.0)
    
    enable_langsmith: bool = Field(default=True)
    log_all_states: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
