import asyncio
import os
import re
from typing import List, Optional

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from langgraph.types import Command

from backend.database import engine, SessionLocal
from backend.models import (
    Base,
    Clause,
    RiskFlag,
    ReviewDecision
)
from backend.crud import (
    create_document,
    get_documents,
    get_document_by_id,
    update_document,
    delete_document,
    get_next_analysis_run_id,
    create_clause,
    create_clauses_batch,
    create_risk_flag,
    create_risk_flags_batch,
    create_review_decision,
    get_clauses,
    get_risk_flags,
    get_review_decisions
)

from graph.graph import graph
from graph.nodes import analysis_progress, document_qa, analyze_realtime_clause
from rag.document_retriever import cleanup_document_vector_store

app = FastAPI(
    title = "Tata AI Legal Document Intelligence API",
    version = "1.1.0"
)

# ----------------------------------------------
# CORS Middleware
# ----------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# ----------------------------------------------
# Request Models
# ----------------------------------------------

class GraphRequest(BaseModel):
    document_id: int
    document_path: str
    user_query: str
    thread_id: str


class ReviewRequest(BaseModel):
    decision: str
    thread_id: str

class DocumentQARequest(BaseModel):
    document_vector_store_path: str
    user_question: str

class ClauseAnalysisRequest(BaseModel):
    clause_text: str
    contract_type: Optional[str] = "Commercial Contract"
    language: Optional[str] = "English"

# ----------------------------------------------
# Create Database Tables
# ----------------------------------------------

Base.metadata.create_all(bind = engine)

# ----------------------------------------------
# Basic API Routing
# ----------------------------------------------

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Tata AI Legal Document Intelligence API",
        "version": "1.1.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

# ----------------------------------------------
# Document Q&A
# ----------------------------------------------

@app.post("/document-qa")
async def ask_document_question(request: DocumentQARequest):
    answer = await asyncio.to_thread(
        document_qa,
        request.document_vector_store_path,
        request.user_question
    )

    return {
        "answer": answer
    }

# ----------------------------------------------
# Real-Time Open-World Clause Analysis
# ----------------------------------------------

@app.post("/analyze-clause")
async def analyze_clause(request: ClauseAnalysisRequest):
    if not request.clause_text.strip():
        raise HTTPException(status_code=400, detail="Clause text cannot be empty.")

    result = await asyncio.to_thread(
        analyze_realtime_clause,
        request.clause_text,
        request.contract_type or "Commercial Contract",
        request.language or "English"
    )

    return result

# ----------------------------------------------
# Analysis Progress
# ----------------------------------------------

@app.get("/analysis-progress/{thread_id}")
def get_analysis_progress(thread_id: str):
    return {
        "thread_id": thread_id,
        "stage": analysis_progress.get(thread_id, "starting")
    }

# ----------------------------------------------
# Database Session Dependency
# ----------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------
# Upload Document with Security Validations
# ----------------------------------------------

MAX_UPLOAD_SIZE = 50 * 1024 * 1024 # 50 MB limit

@app.post("/documents")
async def add_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Sanitize filename against directory traversal
    raw_name = os.path.basename(file.filename)
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', raw_name)
    if not safe_name:
        safe_name = "uploaded_document"

    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", safe_name)

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {MAX_UPLOAD_SIZE // (1024 * 1024)}MB."
        )

    with open(file_path, "wb") as output_file:
        output_file.write(content)

    document = create_document(
        db = db,
        file_name = safe_name,
        file_path = file_path
    )

    return {
        "id": document.id,
        "file_name": document.file_name,
        "status": document.status,
        "file_path": file_path
    }

# ----------------------------------------------
# Document CRUD Endpoints
# ----------------------------------------------

@app.get("/documents")
def read_documents(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    documents = get_documents(db, limit=limit, offset=offset)
    return [
        {
            "id": document.id,
            "file_name": document.file_name,
            "document_type": document.document_type,
            "status": document.status,
            "final_summary": document.final_summary,
            "uploaded_at": document.uploaded_at
        }
        for document in documents
    ]

@app.get("/documents/{document_id}")
def read_single_document(document_id: int, db: Session = Depends(get_db)):
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "file_name": doc.file_name,
        "document_type": doc.document_type,
        "status": doc.status,
        "final_summary": doc.final_summary,
        "file_path": doc.file_path,
        "uploaded_at": doc.uploaded_at
    }

@app.delete("/documents/{document_id}")
def remove_document(document_id: int, db: Session = Depends(get_db)):
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clean up file on disk if it exists
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    deleted = delete_document(db, document_id)
    return {"message": "Document and all associated records deleted", "success": deleted}

# ----------------------------------------------
# Get Clauses with Filtering & Pagination
# ----------------------------------------------

@app.get("/clauses")
def read_clauses(
    document_id: Optional[int] = None,
    analysis_run_id: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    clauses = get_clauses(db, document_id=document_id, analysis_run_id=analysis_run_id, limit=limit, offset=offset)
    return [
        {
            "id": clause.id,
            "document_id": clause.document_id,
            "analysis_run_id": clause.analysis_run_id,
            "clause_type": clause.clause_type,
            "clause_text": clause.clause_text
        }
        for clause in clauses
    ]

# ----------------------------------------------
# Get Risk Flags with Filtering & Pagination
# ----------------------------------------------

@app.get("/risk-flags")
def read_risk_flags(
    document_id: Optional[int] = None,
    analysis_run_id: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    risk_flags = get_risk_flags(db, document_id=document_id, analysis_run_id=analysis_run_id, limit=limit, offset=offset)
    return [
        {
            "id": risk.id,
            "document_id": risk.document_id,
            "analysis_run_id": risk.analysis_run_id,
            "severity": risk.severity,
            "risk_type": risk.risk_type,
            "affected_clause": risk.affected_clause,
            "rationale": risk.rationale,
            "source_location": risk.source_location,
            "recommended_action": risk.recommended_action,
            "confidence": risk.confidence
        }
        for risk in risk_flags
    ]

# ----------------------------------------------
# Get Review Decisions with Filtering & Pagination
# ----------------------------------------------

@app.get("/review-decisions")
def read_review_decisions(
    document_id: Optional[int] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    review_decisions = get_review_decisions(db, document_id=document_id, limit=limit, offset=offset)
    return [
        {
            "id": review.id,
            "document_id": review.document_id,
            "analysis_run_id": review.analysis_run_id,
            "decision": review.decision,
            "reviewed_at": review.reviewed_at
        }
        for review in review_decisions
    ]

# ----------------------------------------------
# Update Document Status
# ----------------------------------------------

@app.put("/documents/{document_id}/status")
def change_document_status(
    document_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    document = update_document(
        db = db,
        document_id = document_id,
        status = status
    )

    if document is None:
        return {"message": "Document not found"}

    return {
        "id": document.id,
        "file_name": document.file_name,
        "status": document.status
    }

# ----------------------------------------------
# Helper: Save Clauses (Batch optimized)
# ----------------------------------------------

def save_clauses(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    clauses: list
):
    if not clauses:
        return
    create_clauses_batch(
        db = db,
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        clauses = clauses
    )

# ----------------------------------------------
# Helper: Save Risk Flags (Batch optimized)
# ----------------------------------------------

def save_risk_flags(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    risk_flags: list
):
    if not risk_flags:
        return
    create_risk_flags_batch(
        db = db,
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        risk_flags = risk_flags
    )

# ----------------------------------------------
# Run Legal Document Analysis (Non-blocking async)
# ----------------------------------------------

@app.post("/run-analysis")
async def run_analysis(
    request: GraphRequest,
    db: Session = Depends(get_db)
):
    # Create a new analysis run for this document
    analysis_run_id = get_next_analysis_run_id(
        db,
        request.document_id
    )

    initial_state = {
        "document_path": request.document_path,
        "user_query": request.user_query,
        "analysis_run_id": analysis_run_id,
        "thread_id": request.thread_id
    }

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    # Update document status
    update_document(
        db = db,
        document_id = request.document_id,
        status = "analyzing"
    )

    # Run LangGraph synchronously in a thread pool to avoid blocking FastAPI
    result = await asyncio.to_thread(
        graph.invoke,
        initial_state,
        config = config
    )

    # --------------------------------------------------
    # Detect LangGraph interrupt
    # --------------------------------------------------

    if "__interrupt__" in result:
        interrupt_payload = result["__interrupt__"][0].value

        save_clauses(
            db = db,
            document_id = request.document_id,
            analysis_run_id = analysis_run_id,
            clauses = result.get("clauses", [])
        )

        save_risk_flags(
            db = db,
            document_id = request.document_id,
            analysis_run_id = analysis_run_id,
            risk_flags = result.get("risk_flags", [])
        )

        update_document(
            db = db,
            document_id = request.document_id,
            status = "awaiting_human_review",
            document_type = result.get("document_type")
        )

        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "document_type": result.get("document_type"),
            "document_vector_store_path": result.get("document_vector_store_path"),
            "clauses": result.get("clauses"),
            "risk_flags": result.get("risk_flags"),
            "human_review_status": "pending",
            "human_review_request": interrupt_payload,
            "final_summary": None
        }

    # --------------------------------------------------
    # Handle Early Exit Outcomes
    # --------------------------------------------------

    if result.get("query_allowed") is False:
        update_document(
            db = db,
            document_id = request.document_id,
            status = "rejected"
        )
        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "status": "rejected",
            "message": result.get(
                "query_guardrail_message",
                "The request is outside the supported scope."
            ),
            "document_type": None,
            "clauses": [],
            "risk_flags": [],
            "human_review_status": None,
            "human_review_request": None,
            "final_summary": None
        }

    if result.get("parsing_error") is True:
        update_document(
            db = db,
            document_id = request.document_id,
            status = "failed"
        )
        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "status": "failed",
            "message": result.get(
                "parsing_error_message",
                "The document could not be processed."
            ),
            "document_type": None,
            "clauses": [],
            "risk_flags": [],
            "human_review_status": None,
            "human_review_request": None,
            "final_summary": None
        }

    if result.get("is_sufficient") is False:
        update_document(
            db = db,
            document_id = request.document_id,
            status = "insufficient_information"
        )
        return {
            "document_id": request.document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": analysis_run_id,
            "status": "insufficient_information",
            "message": "The document does not contain enough information for the requested review.",
            "missing_information": result.get("missing_information", []),
            "reasoning": result.get("reasoning", ""),
            "document_type": None,
            "clauses": result.get("clauses", []),
            "risk_flags": [],
            "human_review_status": None,
            "human_review_request": None,
            "final_summary": None
        }

    # --------------------------------------------------
    # Normal completion
    # --------------------------------------------------

    save_clauses(
        db = db,
        document_id = request.document_id,
        analysis_run_id = analysis_run_id,
        clauses = result.get("clauses", [])
    )

    save_risk_flags(
        db = db,
        document_id = request.document_id,
        analysis_run_id = analysis_run_id,
        risk_flags = result.get("risk_flags", [])
    )

    update_document(
        db = db,
        document_id = request.document_id,
        status = "completed",
        document_type = result.get("document_type"),
        final_summary = result.get("final_summary")
    )

    return {
        "document_id": request.document_id,
        "thread_id": request.thread_id,
        "analysis_run_id": analysis_run_id,
        "status": "completed",
        "document_type": result.get("document_type"),
        "document_vector_store_path": result.get("document_vector_store_path"),
        "clauses": result.get("clauses"),
        "risk_flags": result.get("risk_flags"),
        "human_review_status": result.get("human_review_status"),
        "human_review_request": None,
        "final_summary": result.get("final_summary")
    }

# ----------------------------------------------
# Human Review
# ----------------------------------------------

@app.post("/documents/{document_id}/review")
async def submit_review(
    document_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db)
):
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    current_state = graph.get_state(config).values
    current_run_id = current_state.get("analysis_run_id")

    if current_run_id is None:
        current_run_id = get_next_analysis_run_id(
            db,
            document_id
        )

    create_review_decision(
        db = db,
        document_id = document_id,
        analysis_run_id = current_run_id,
        decision = request.decision
    )

    new_run_id = current_run_id

    if request.decision in ["re-analyze", "wrong_classification"]:
        new_run_id = get_next_analysis_run_id(db, document_id)
        graph.update_state(config, {"analysis_run_id": new_run_id})
        analysis_progress[request.thread_id] = "starting"

    # Resume graph execution asynchronously
    result = await asyncio.to_thread(
        graph.invoke,
        Command(resume = request.decision),
        config = config
    )

    if "__interrupt__" in result:
        interrupt_payload = result["__interrupt__"][0].value

        save_clauses(
            db = db,
            document_id = document_id,
            analysis_run_id = new_run_id,
            clauses = result.get("clauses", [])
        )

        save_risk_flags(
            db = db,
            document_id = document_id,
            analysis_run_id = new_run_id,
            risk_flags = result.get("risk_flags", [])
        )

        update_document(
            db = db,
            document_id = document_id,
            status = "awaiting_human_review",
            document_type = result.get("document_type")
        )

        return {
            "document_id": document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": new_run_id,
            "decision": request.decision,
            "document_type": result.get("document_type"),
            "document_vector_store_path": result.get("document_vector_store_path"),
            "clauses": result.get("clauses"),
            "risk_flags": result.get("risk_flags"),
            "human_review_status": "pending",
            "human_review_request": interrupt_payload,
            "final_summary": None
        }

    if request.decision == "escalate":
        update_document(
            db = db,
            document_id = document_id,
            status = "escalated",
            document_type = result.get("document_type")
        )
        return {
            "document_id": document_id,
            "thread_id": request.thread_id,
            "analysis_run_id": new_run_id,
            "decision": request.decision,
            "status": "escalated",
            "document_type": result.get("document_type"),
            "clauses": result.get("clauses"),
            "risk_flags": result.get("risk_flags"),
            "human_review_status": "escalated",
            "human_review_request": None,
            "final_summary": None
        }

    # Decision: approve
    update_document(
        db = db,
        document_id = document_id,
        status = "approved",
        document_type = result.get("document_type"),
        final_summary = result.get("final_summary")
    )

    return {
        "document_id": document_id,
        "thread_id": request.thread_id,
        "analysis_run_id": new_run_id,
        "decision": request.decision,
        "status": "approved",
        "document_type": result.get("document_type"),
        "document_vector_store_path": result.get("document_vector_store_path"),
        "clauses": result.get("clauses"),
        "risk_flags": result.get("risk_flags"),
        "human_review_status": "approved",
        "human_review_request": None,
        "final_summary": result.get("final_summary")
    }
