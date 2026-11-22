# --------------------------------------------------
# Functional Workflow Tests
# --------------------------------------------------

import unittest

class TestWorkflowModules(unittest.TestCase):

    def test_project_modules_import(self):
        from graph.graph import graph
        from graph.nodes import parse_document
        from rag.document_retriever import create_document_vector_store
        from rag.kb_retriever import get_kb_retriever
        from rag.embeddings import get_embeddings

        self.assertIsNotNone(graph)
        self.assertIsNotNone(parse_document)
        self.assertIsNotNone(create_document_vector_store)
        self.assertIsNotNone(get_kb_retriever)
        self.assertIsNotNone(get_embeddings)

    def test_database_crud_methods(self):
        from backend.database import SessionLocal, engine, Base
        from backend.crud import (
            create_document,
            get_documents,
            get_document_by_id,
            create_clauses_batch,
            create_risk_flags_batch,
            delete_document
        )

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            doc = create_document(db, "test_contract.pdf", "uploads/test_contract.pdf")
            self.assertIsNotNone(doc.id)

            fetched = get_document_by_id(db, doc.id)
            self.assertEqual(fetched.file_name, "test_contract.pdf")

            clauses = create_clauses_batch(db, doc.id, 1, [{"clause_name": "Governing Law", "clause_text": "Laws of India"}])
            self.assertEqual(len(clauses), 1)

            deleted = delete_document(db, doc.id)
            self.assertTrue(deleted)
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
