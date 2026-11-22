# ===================================================================================================
# Tools used by the Legal Review Agent to search and verify evidence from the uploaded document.
# ===================================================================================================

import re
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langchain_chroma import Chroma

from graph.state import Legal_Document_State
from rag.embeddings import get_embeddings

def get_document_retriever(state: Legal_Document_State, k: int = 3):
    vector_store = Chroma(
        persist_directory = state["document_vector_store_path"],
        embedding_function = get_embeddings()
    )

    return vector_store.as_retriever(
        search_kwargs = {"k": k}
    )

# --------------------------------------------------
# Document Evidence Search Tool
# --------------------------------------------------

@tool
def document_evidence_search(
    query: str,
    state: Annotated[Legal_Document_State, InjectedState]) -> str:
    """
    Search the uploaded document for relevant evidence using semantic search.
    The agent should use this tool when additional document evidence is required.
    """
    retriever = get_document_retriever(state, k=3)
    results = retriever.invoke(query)

    if not results:
        return "No relevant evidence was found in the document for the query."

    evidence = []
    for idx, result in enumerate(results, start=1):
        evidence.append(
            f"[Evidence #{idx}]\n{result.page_content.strip()}\n"
        )

    return "\n---\n".join(evidence)

# --------------------------------------------------
# Evidence Verification Tool
# --------------------------------------------------

@tool
def evidence_verification(
    claim_or_provision: str,
    state: Annotated[Legal_Document_State, InjectedState]) -> str:
    """
    Verify whether a specific claim, obligation, or risk condition is substantiated by the uploaded document.
    Performs semantic retrieval plus keyword cross-checking to confirm or refute the assertion.
    """
    retriever = get_document_retriever(state, k=4)
    results = retriever.invoke(claim_or_provision)

    if not results:
        return f"VERIFICATION RESULT: UNVERIFIED\nNo relevant provisions found regarding: '{claim_or_provision}'."

    # Extract key terms from claim (words of 4+ characters)
    keywords = set(re.findall(r"\b[a-zA-Z]{4,}\b", claim_or_provision.lower()))
    matches_found = []

    for idx, doc in enumerate(results, start=1):
        content = doc.page_content
        content_lower = content.lower()
        matched_words = [kw for kw in keywords if kw in content_lower]
        match_ratio = len(matched_words) / max(len(keywords), 1)

        matches_found.append({
            "index": idx,
            "text": content.strip(),
            "match_ratio": match_ratio,
            "matched_terms": matched_words[:5]
        })

    # Sort by match strength
    matches_found.sort(key=lambda x: x["match_ratio"], reverse=True)
    best_match = matches_found[0]

    status = "VERIFIED / SUPPORTED" if best_match["match_ratio"] >= 0.4 else "PARTIALLY SUPPORTED / AMBIGUOUS"
    if best_match["match_ratio"] < 0.15:
        status = "WEAK EVIDENCE / NOT EXPLICITLY FOUND"

    verification_output = [
        f"VERIFICATION STATUS: {status}",
        f"Assessed Claim: '{claim_or_provision}'",
        f"Key matched terms: {', '.join(best_match['matched_terms']) or 'None'}",
        "\nMost relevant document excerpt:",
        best_match["text"]
    ]

    return "\n".join(verification_output)
