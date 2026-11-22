from langchain_chroma import Chroma
from rag.embeddings import get_embeddings

# --------------------------------------------------
# Cached Knowledge Base Retriever
# --------------------------------------------------

_cached_retriever = None

def get_kb_retriever(persist_directory: str = "vector_store/chroma_db", k: int = 2):
    """
    Returns a cached retriever for the legal knowledge base ChromaDB.
    """
    global _cached_retriever

    if _cached_retriever is None:
        embedding_model = get_embeddings()

        vector_store = Chroma(
            persist_directory = persist_directory,
            embedding_function = embedding_model
        )

        _cached_retriever = vector_store.as_retriever(
            search_kwargs = {"k": k}
        )

    return _cached_retriever
