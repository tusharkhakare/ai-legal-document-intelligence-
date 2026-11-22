# ==========================================================================================
# Creates a semantic retriever for the uploaded document.
# The parsed document text is chunked, embedded, and stored in a temporary vector store.
# This retriever will later be used by the Evidence Search and Verification tools.
# ==========================================================================================
import atexit
import os
import shutil
import tempfile

from langchain_core.documents import Document
from langchain_chroma import Chroma

from graph.state import Legal_Document_State
from rag.embeddings import get_embeddings
from utils.chunking import create_chunks

# Registry of active temporary vector stores to prevent disk leaks
_active_temp_directories = set()

def cleanup_document_vector_store(directory_path: str):
    """
    Safely delete a temporary vector store directory when analysis finishes.
    """
    if directory_path and os.path.exists(directory_path):
        try:
            shutil.rmtree(directory_path, ignore_errors=True)
            _active_temp_directories.discard(directory_path)
        except Exception:
            pass

def cleanup_all_temp_vector_stores():
    """Clean up all active temporary stores on application shutdown."""
    for path in list(_active_temp_directories):
        cleanup_document_vector_store(path)

atexit.register(cleanup_all_temp_vector_stores)

# --------------------------------------------------
# Create Document Retriever
# --------------------------------------------------

def create_document_vector_store(state: Legal_Document_State):
    raw_text = state["raw_text"]

    # Split the already-parsed document text into smaller chunks
    chunks = create_chunks(raw_text)

    # Convert each chunk into a LangChain Document with metadata
    documents = []
    for idx, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content = chunk,
                metadata = {"chunk_index": idx}
            )
        )

    # Create a temporary directory for this uploaded document
    temp_directory = tempfile.mkdtemp(prefix="tata_legal_vs_")
    _active_temp_directories.add(temp_directory)

    # Create Chroma vector store inside the temporary directory
    Chroma.from_documents(
        documents = documents,
        embedding = get_embeddings(),
        persist_directory = temp_directory
    )

    return {
        "document_vector_store_path": temp_directory
    }
