import os
from pathlib import Path
from typing import Optional

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent

# ============================================================================
# FILE PATHS
# ============================================================================
DATA_FILE: str = "sistec_rag_data.md"
CACHE_DIR: Path = PROJECT_ROOT / ".cache"
LOG_FILE: Path = PROJECT_ROOT / "chatbot.log"

# ============================================================================
# API CONFIGURATION
# ============================================================================
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ============================================================================
# LANGUAGE MODEL CONFIGURATION
# ============================================================================
EMBED_MODEL: str = "BAAI/bge-base-en-v1.5"
RERANK_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# ============================================================================
# TEXT PROCESSING CONFIGURATION
# ============================================================================
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 150))

# ============================================================================
# RETRIEVAL CONFIGURATION
# ============================================================================
BM25_TOP_K: int = int(os.getenv("BM25_TOP_K", 10))
FAISS_TOP_K: int = int(os.getenv("FAISS_TOP_K", 10))
RERANK_TOP_K: int = int(os.getenv("RERANK_TOP_K", 5))

# Reciprocal Rank Fusion weight (BM25: 1-ALPHA, FAISS: ALPHA)
ALPHA: float = float(os.getenv("ALPHA", 0.5))

# ============================================================================
# VOICE CONFIGURATION
# ============================================================================
VOICE_DURATION: int = 5  # Default recording duration in seconds
VOICE_LANGUAGE: str = "en"
AUDIO_FILE: str = "response.mp3"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# UI CONFIGURATION
# ============================================================================
ENABLE_VOICE_OUTPUT: bool = os.getenv("ENABLE_VOICE_OUTPUT", "true").lower() == "true"
SHOW_CONTEXT: bool = os.getenv("SHOW_CONTEXT", "false").lower() == "true"

# Create cache directory if it doesn't exist
CACHE_DIR.mkdir(exist_ok=True, parents=True)
