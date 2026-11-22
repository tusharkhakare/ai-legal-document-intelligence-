# ⚖️ AI Legal Document Intelligence

**Tushar Vijay Khakare**

A lightweight, production‑ready AI‑assisted legal document analysis system. It extracts clauses, verifies evidence, classifies documents, and produces a concise risk‑aware summary — all while keeping a human reviewer in the loop.

---

## 📦 Project Overview

- **Purpose** – Automate the initial review of legal contracts and policy documents, surface key clauses, assess sufficiency of information, and flag potential risks. The system is *assistive*; final decisions must be made by a qualified professional.
- **License** – MIT (see `LICENSE`).
- **Author** – Tushar Vijay Khakare.
- **Live Demo** – Not included; deploy locally or with Docker (see below).

---

## 🚀 Quick Start (Docker)

```bash
# Build and run with Docker Compose
docker compose up --build
```

The Streamlit UI will be available at `http://localhost:8501` and the FastAPI backend at `http://localhost:8000`.

---

## 🛠️ Architecture & Workflow

```text
Document Upload
       │
       ↓
Document Parsing
       │
       ↓
Temporary Document Vector Store
       │
       ↓
Clause Extraction
       │
       ↓
Sufficiency Check
   /             \
  /               \
Insufficient   Sufficient
   │                │
   ↓                ↓
Show Missing Info   Document Classification
   │                │
   ↓                ↓
  END           Knowledge Base Retrieval
                        │
                        ↓
                 Legal Review Agent
                   /           \
                  ↓             ↓
          Document Evidence   Evidence
               Search         Verification
                    \           /
                     \         /
                      ↓       ↓
                 Legal Findings
                       │
                       ↓
                 Risk Analysis
                       │
                       ↓
                 Human Review
                       │
      ┌───────────────────┬───────┼───────────────┐
      ↓                   ↓       ↓               ↓
   Approve            Re-analyze  Wrong        Escalate
                                 Classification
      │                   │       │               │
      │                   ↓       ↓               ↓
      │             Retrieve   Reclassify       END
      │             Guidance      │
      │                   │       │
      │                   ↓       │
      │             Legal Review │
      │                Agent ◄────┘
      │
      ↓
Final Legal Document
      Summary
```

1. **Upload** – User uploads PDF/DOCX/ODT/PNG/JPG.
2. **Parsing** – Text extraction (OCR for images) and chunking.
3. **Vector Store** – Temporary in‑memory ChromaDB for the uploaded file.
4. **Clause Extraction** – LLM generates structured clause list.
5. **Sufficiency Check** – Ensures required information is present; otherwise stops.
6. **Classification** – Determines document type (vendor agreement, policy, etc.).
7. **Knowledge‑Base Retrieval** – Retrieves relevant guidance from the built‑in legal KB.
8. **Legal Review Agent** – Runs a LangGraph workflow that uses the extracted clauses, retrieved guidance, and evidence tools.
9. **Evidence Search & Verification** – Retrieves and validates document excerpts.
10. **Risk Analysis** – Flags missing, ambiguous, or high‑risk provisions.
11. **Human‑in‑the‑Loop** – Reviewer can Approve, Re‑analyse, Re‑classify, or Escalate.
12. **Final Summary** – Structured output containing classification, key clauses, risks, and supporting evidence.

---

## 📂 Key Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit front‑end UI |
| `backend/main.py` | FastAPI server exposing endpoints |
| `graph/graph.py` | LangGraph workflow definition |
| `rag/*` | Retrieval‑augmented generation utilities |
| `tests/` | Unit and integration tests |
| `Dockerfile`, `docker‑compose.yml` | Containerised deployment |

---

## 🧪 Testing

```bash
python run_tests.py   # or
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🔐 Security & Data

- All secrets are loaded from environment variables (`.env.example` provided).
- `.env`, SQLite DB files, and temporary vector stores are excluded via `.gitignore`.
- No proprietary data is stored in the repository.

---

## ⚖️ Disclaimer

This project is for **educational and portfolio** purposes only. It should **not** replace professional legal counsel. Results are AI‑generated and may contain errors; always perform a manual review.
