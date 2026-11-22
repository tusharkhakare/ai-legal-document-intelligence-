# --------------------------------------------------
# Document Processing Tests
# --------------------------------------------------

import os
import unittest
from pathlib import Path

class TestDocumentProcessing(unittest.TestCase):

    def test_document_processing_modules_import(self):
        from graph.nodes import (
            parse_document,
            parse_pdf,
            parse_docx,
            parse_image,
            extract_text_from_image,
            parse_odt
        )

        self.assertIsNotNone(parse_document)
        self.assertIsNotNone(parse_pdf)
        self.assertIsNotNone(parse_docx)
        self.assertIsNotNone(parse_image)
        self.assertIsNotNone(extract_text_from_image)
        self.assertIsNotNone(parse_odt)

    def test_parse_pdf_file(self):
        from graph.nodes import parse_pdf
        sample_pdf = Path("tests/testing_files/pdf_testing.pdf")
        if sample_pdf.exists():
            text = parse_pdf(str(sample_pdf))
            self.assertIsInstance(text, str)
            self.assertTrue(len(text.strip()) > 0, "PDF should yield non-empty text")

    def test_parse_docx_file(self):
        from graph.nodes import parse_docx
        sample_docx = Path("tests/testing_files/docx_testing.docx")
        if sample_docx.exists():
            text = parse_docx(str(sample_docx))
            self.assertIsInstance(text, str)
            self.assertTrue(len(text.strip()) > 0, "DOCX should yield non-empty text")

    def test_parse_odt_file(self):
        from graph.nodes import parse_odt
        sample_odt = Path("tests/testing_files/odt_testing.odt")
        if sample_odt.exists():
            text = parse_odt(str(sample_odt))
            self.assertIsInstance(text, str)
            self.assertTrue(len(text.strip()) > 0, "ODT should yield non-empty text")

if __name__ == "__main__":
    unittest.main()
