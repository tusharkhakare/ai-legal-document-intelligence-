"""
Script to create / update ChromaDB vector store from knowledge base markdown files.
Can be executed directly from root or from within rag/ directory.
"""

import os
import sys

# Ensure root directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from langchain_chroma import Chroma
from rag.embeddings import get_embeddings
from rag.kb_loader import load_knowledge_base

def build_kb_embeddings(kb_dir: str = "knowledge_base", persist_dir: str = "vector_store/chroma_db"):
    print(f"Loading knowledge base from: {kb_dir}...")
    documents = load_knowledge_base(kb_dir)
    print(f"Loaded {len(documents)} knowledge base guidance entries.")

    embeddings = get_embeddings()

    print(f"Writing embeddings to ChromaDB at: {persist_dir}...")
    vector_store = Chroma.from_documents(
        documents = documents,
        embedding = embeddings,
        persist_directory = persist_dir
    )
    print("Knowledge base vector store successfully created / updated!")
    return vector_store

if __name__ == "__main__":
    build_kb_embeddings()
