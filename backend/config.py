"""
Follow-up Reply Assistant - Configuration Module
Project Code: PRJ-042 | Student: SIVASURYA.B PSVPEC (411723205052)
Domain: Business | Focus: GenAI | Recommended Stack: FastAPI + LangChain + Streamlit + Chroma
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    # Project Identity
    PROJECT_CODE: str = "PRJ-042"
    PROJECT_NAME: str = "Follow-up Reply Assistant"
    STUDENT_NAME: str = "SIVASURYA.B PSVPEC"
    REG_NO: str = "411723205052"
    DEPARTMENT: str = "IT"
    EMAIL: str = "sivasurya.b.27.it@psvpec.in"
    APP_VERSION: str = "1.0.0"

    # Server Settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Storage & Paths
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLE_DIR: Path = BASE_DIR / "data" / "sample_meetings"
    CHROMA_PERSIST_DIR: Path = BASE_DIR / "data" / "chroma_db"
    TEMPLATE_DIR: Path = BASE_DIR / "data" / "templates"
    HISTORY_FILE: Path = BASE_DIR / "data" / "history.json"
    CHROMA_COLLECTION_NAME: str = "followup_replies_kb"

    # LLM Settings
    LLM_PROVIDER: str = "mock"  # "mock" (offline standalone), "openai", "gemini"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-1.5-flash"

    # RAG Settings
    CHUNK_SIZE: int = 400
    CHUNK_OVERLAP: int = 80
    RETRIEVAL_TOP_K: int = 4

    # Security
    ADMIN_API_KEY: str = "admin_secure_key_prj042"

# Singleton settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
