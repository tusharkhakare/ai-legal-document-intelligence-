from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models import Clause, Document, ReviewDecision, RiskFlag

# ----------------------------------------------
# Document CRUD
# ----------------------------------------------

def create_document(db: Session, file_name: str, file_path: str = None) -> Document:
    """Create a new document record."""
    document = Document(
        file_name = file_name,
        file_path = file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

def get_documents(db: Session, limit: int = 50, offset: int = 0) -> List[Document]:
    """Get uploaded documents with optional pagination."""
    return db.query(Document).order_by(Document.id.desc()).offset(offset).limit(limit).all()

def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
    """Get a single document by its primary key ID."""
    return db.query(Document).filter(Document.id == document_id).first()

def update_document(
    db: Session,
    document_id: int,
    status: str = None,
    document_type: str = None,
    final_summary: str = None,
    file_path: str = None
) -> Optional[Document]:
    """Update a document's fields."""
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if document:
        if status is not None:
            document.status = status

        if document_type is not None:
            document.document_type = document_type

        if final_summary is not None:
            document.final_summary = final_summary

        if file_path is not None:
            document.file_path = file_path

        db.commit()
        db.refresh(document)

    return document

def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document and all associated clauses/risks/reviews (via cascade)."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if document:
        db.delete(document)
        db.commit()
        return True
    return False

# ----------------------------------------------
# Analysis Run ID Helper
# ----------------------------------------------

def get_next_analysis_run_id(db: Session, document_id: int) -> int:
    """Find next sequential analysis run ID for a document."""
    max_clause = db.query(
        func.max(Clause.analysis_run_id)
    ).filter(Clause.document_id == document_id).scalar()

    max_risk = db.query(
        func.max(RiskFlag.analysis_run_id)
    ).filter(RiskFlag.document_id == document_id).scalar()

    max_review = db.query(
        func.max(ReviewDecision.analysis_run_id)
    ).filter(ReviewDecision.document_id == document_id).scalar()

    existing = [v for v in [max_clause, max_risk, max_review] if v is not None]

    if not existing:
        return 1

    return max(existing) + 1

# ----------------------------------------------
# Clause CRUD
# ----------------------------------------------

def create_clause(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    clause_type: str,
    clause_text: str
) -> Clause:
    """Create a single clause record."""
    clause = Clause(
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        clause_type = clause_type,
        clause_text = clause_text
    )

    db.add(clause)
    db.commit()
    db.refresh(clause)

    return clause

def create_clauses_batch(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    clauses: list
) -> List[Clause]:
    """Batch-insert multiple extracted clauses in a single database transaction."""
    clause_objects = []
    for c in clauses:
        c_type = getattr(c, "clause_name", None) or (c.get("clause_name") if isinstance(c, dict) else str(c))
        c_text = getattr(c, "clause_text", None) or (c.get("clause_text") if isinstance(c, dict) else "")

        clause_obj = Clause(
            document_id = document_id,
            analysis_run_id = analysis_run_id,
            clause_type = c_type,
            clause_text = c_text
        )
        clause_objects.append(clause_obj)

    if clause_objects:
        db.add_all(clause_objects)
        db.commit()

    return clause_objects

def get_clauses(
    db: Session,
    document_id: Optional[int] = None,
    analysis_run_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Clause]:
    """Retrieve clauses with optional document and run filtering and pagination."""
    query = db.query(Clause)
    if document_id is not None:
        query = query.filter(Clause.document_id == document_id)
    if analysis_run_id is not None:
        query = query.filter(Clause.analysis_run_id == analysis_run_id)
    return query.offset(offset).limit(limit).all()

# ----------------------------------------------
# RiskFlag CRUD
# ----------------------------------------------

def create_risk_flag(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    severity: str,
    risk_type: str,
    affected_clause: str,
    rationale: str,
    source_location: str,
    recommended_action: str,
    confidence: int
) -> RiskFlag:
    """Create a single risk flag record."""
    risk_flag = RiskFlag(
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        severity = severity,
        risk_type = risk_type,
        affected_clause = affected_clause,
        rationale = rationale,
        source_location = source_location,
        recommended_action = recommended_action,
        confidence = confidence
    )

    db.add(risk_flag)
    db.commit()
    db.refresh(risk_flag)

    return risk_flag

def create_risk_flags_batch(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    risk_flags: list
) -> List[RiskFlag]:
    """Batch-insert multiple risk flags in a single transaction."""
    risk_objects = []
    for r in risk_flags:
        if isinstance(r, dict):
            severity = r.get("severity")
            risk_type = r.get("risk_type")
            affected_clause = r.get("affected_clause")
            rationale = r.get("rationale")
            source_location = r.get("source_location")
            recommended_action = r.get("recommended_action")
            confidence = r.get("confidence")
        else:
            severity = getattr(r, "severity", None)
            risk_type = getattr(r, "risk_type", None)
            affected_clause = getattr(r, "affected_clause", None)
            rationale = getattr(r, "rationale", None)
            source_location = getattr(r, "source_location", None)
            recommended_action = getattr(r, "recommended_action", None)
            confidence = getattr(r, "confidence", None)

        risk_obj = RiskFlag(
            document_id = document_id,
            analysis_run_id = analysis_run_id,
            severity = severity,
            risk_type = risk_type,
            affected_clause = affected_clause,
            rationale = rationale,
            source_location = source_location,
            recommended_action = recommended_action,
            confidence = confidence
        )
        risk_objects.append(risk_obj)

    if risk_objects:
        db.add_all(risk_objects)
        db.commit()

    return risk_objects

def get_risk_flags(
    db: Session,
    document_id: Optional[int] = None,
    analysis_run_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[RiskFlag]:
    """Retrieve risk flags with optional filtering and pagination."""
    query = db.query(RiskFlag)
    if document_id is not None:
        query = query.filter(RiskFlag.document_id == document_id)
    if analysis_run_id is not None:
        query = query.filter(RiskFlag.analysis_run_id == analysis_run_id)
    return query.offset(offset).limit(limit).all()

# ----------------------------------------------
# ReviewDecision CRUD
# ----------------------------------------------

def create_review_decision(
    db: Session,
    document_id: int,
    analysis_run_id: int,
    decision: str
) -> ReviewDecision:
    """Create a single review decision record."""
    review_decision = ReviewDecision(
        document_id = document_id,
        analysis_run_id = analysis_run_id,
        decision = decision
    )

    db.add(review_decision)
    db.commit()
    db.refresh(review_decision)

    return review_decision

def get_review_decisions(
    db: Session,
    document_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0
) -> List[ReviewDecision]:
    """Retrieve review decisions with optional filtering."""
    query = db.query(ReviewDecision)
    if document_id is not None:
        query = query.filter(ReviewDecision.document_id == document_id)
    return query.order_by(ReviewDecision.id.desc()).offset(offset).limit(limit).all()
