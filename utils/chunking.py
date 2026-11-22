# ========================================================================================================
# File to create chunks - Legal-aware text chunking for better retrieval and summary generation.
# ========================================================================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Legal document section separators ordered by structural hierarchy
LEGAL_SEPARATORS = [
    "\n\n\n",
    "\n\n",
    "\nARTICLE ",
    "\nArticle ",
    "\nSECTION ",
    "\nSection ",
    "\nCLAUSE ",
    "\nClause ",
    r"\n(?=[0-9]+\.[0-9]+)",  # Numbered clauses like 1.1, 2.3
    r"\n(?=[0-9]+\.)",        # Numbered lists like 1., 2.
    "\n",
    ". ",
    ";\n",
    " ",
    ""
]

def create_chunks(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[str]:
    """
    Split legal document text into coherent chunks, preserving clause and article boundaries.
    """
    if not text:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators = LEGAL_SEPARATORS,
        is_separator_regex = True
    )

    chunks = splitter.split_text(text)
    return chunks
