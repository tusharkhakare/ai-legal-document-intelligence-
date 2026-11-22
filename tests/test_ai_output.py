# --------------------------------------------------
# AI Output Tests
# --------------------------------------------------

import unittest

class TestAIOutputModels(unittest.TestCase):

    def test_ai_output_models_import(self):
        from graph.nodes import (
            Clause,
            Clause_Extraction,
            Sufficiency_Check,
            RiskFlag,
            RiskAnalysisOutput
        )

        self.assertIsNotNone(Clause)
        self.assertIsNotNone(Clause_Extraction)
        self.assertIsNotNone(Sufficiency_Check)
        self.assertIsNotNone(RiskFlag)
        self.assertIsNotNone(RiskAnalysisOutput)

    def test_clause_model_instantiation(self):
        from graph.nodes import Clause
        clause = Clause(clause_name="Termination", clause_text="Either party may terminate upon 30 days notice.")
        self.assertEqual(clause.clause_name, "Termination")
        self.assertIn("30 days notice", clause.clause_text)

    def test_risk_flag_model_instantiation(self):
        from graph.nodes import RiskFlag
        risk = RiskFlag(
            severity="HIGH",
            risk_type="Liability",
            affected_clause="Limitation of Liability",
            rationale="Uncapped liability poses enterprise risk.",
            source_location="Clause 12.1",
            recommended_action="Introduce mutual liability cap.",
            confidence=90
        )
        self.assertEqual(risk.severity, "HIGH")
        self.assertEqual(risk.confidence, 90)

if __name__ == "__main__":
    unittest.main()
