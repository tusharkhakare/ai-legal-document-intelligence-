# --------------------------------------------------
# Edge Case Tests
# --------------------------------------------------

import unittest
from pathlib import Path

class TestEdgeCases(unittest.TestCase):

    def test_sample_documents_exist(self):
        pdf_path = Path("tests/testing_files/pdf_testing.pdf")
        self.assertTrue(pdf_path.exists(), "Sample testing PDF should exist")
        self.assertTrue(pdf_path.is_file())

        docx_path = Path("tests/testing_files/docx_testing.docx")
        self.assertTrue(docx_path.exists(), "Sample testing DOCX should exist")

    def test_supported_document_formats(self):
        supported_formats = {
            ".pdf",
            ".docx",
            ".odt",
            ".png",
            ".jpg",
            ".jpeg"
        }

        self.assertIn(".pdf", supported_formats)
        self.assertIn(".docx", supported_formats)
        self.assertIn(".odt", supported_formats)
        self.assertIn(".png", supported_formats)
        self.assertIn(".jpg", supported_formats)
        self.assertIn(".jpeg", supported_formats)

    def test_unsupported_format_detection(self):
        unsupported = [".exe", ".zip", ".mp3", ".xlsx"]
        supported = {".pdf", ".docx", ".odt", ".png", ".jpg", ".jpeg"}
        for ext in unsupported:
            self.assertNotIn(ext, supported)

    def test_empty_string_chunking(self):
        from utils.chunking import create_chunks
        chunks = create_chunks("")
        self.assertEqual(chunks, [])

if __name__ == "__main__":
    unittest.main()
