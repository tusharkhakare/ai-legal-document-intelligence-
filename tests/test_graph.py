import os
import unittest

class TestGraphWorkflow(unittest.TestCase):

    def test_graph_compilation_and_nodes(self):
        from graph.graph import graph

        # Verify graph is compiled and has the essential expected node names
        self.assertIsNotNone(graph)
        node_names = set(graph.nodes.keys())
        expected_nodes = {
            "check_query_guardrail",
            "parse_document",
            "create_document_vector_store",
            "extract_clauses",
            "check_sufficient_information",
            "document_classification",
            "retrieve_legal_guidance",
            "legal_review_agent",
            "risk_analysis",
            "human_review",
            "final_summary"
        }
        for expected in expected_nodes:
            self.assertIn(expected, node_names)

def run_live_workflow():
    """Manual integration run with live LLM (requires API key)."""
    from graph.graph import graph

    document_path = "tests/testing_files/pdf_testing.pdf"
    initial_state = {"document_path": document_path}

    print("Running complete legal document workflow...\n")
    result = graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": "manual-test-thread"}}
    )
    print("Workflow result keys:", result.keys())

if __name__ == "__main__":
    unittest.main()
