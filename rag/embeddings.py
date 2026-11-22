"""
Centralized, thread-safe embedding model singleton for Tata AI Legal Document Intelligence.
Avoids reloading multiple copies of the heavy HuggingFace sentence-transformers model.
"""

import os
import threading
from langchain_huggingface import HuggingFaceEmbeddings

_embeddings = None
_lock = threading.Lock()

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def get_embeddings(model_name: str = DEFAULT_EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    """
    Returns a shared singleton instance of the HuggingFace embedding model.
    Thread-safe and initialized lazily on first access.
    Prefers cached local weights when available to avoid network delays.
    """
    global _embeddings
    if _embeddings is None:
        with _lock:
            if _embeddings is None:
                try:
                    _embeddings = HuggingFaceEmbeddings(
                        model_name = model_name,
                        model_kwargs = {"local_files_only": True}
                    )
                except Exception:
                    _embeddings = HuggingFaceEmbeddings(
                        model_name = model_name
                    )
    return _embeddings
