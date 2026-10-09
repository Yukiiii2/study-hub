"""Read-only recall mapping and private-cell omission checks, without a database."""
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openpyxl import Workbook


class RecallInspectionChecks(unittest.TestCase):
    def source(self, path):
        book = Workbook()
        sheet = book.active
        sheet.title = "MS Recall"
        for coordinate, value in {"A1": "Topic", "B1": "First Rep", "C2": "R1", "D2": "Rating",
                                  "E2": "R2", "F2": "Rating", "G2": "R3", "H2": "Rating",
                                  "I2": "R4", "J2": "Rating", "K2": "R5", "L2": "Rating",
                                  "M1": "Next Rep", "N1": "Final Rating", "O1": "Remarks",
                                  "A3": "  Working\nCapital  ", "A4": "working capital",
                                  "A5": '=CONCAT("private formula title")', "A6": "Working Capital",
                                  "B3": datetime(2035, 3, 19), "C3": 98765, "D3": "private rating",
                                  "M3": '=B3+SECRET_PRIVATE_FORMULA', "O3": "PRIVATE_REMINDER_91"}.items():
            sheet[coordinate] = value
        book.save(path)
        book.close()

    def test_exact_normalized_subject_title_mapping_does_not_guess_case_or_formula(self):
        from app.parsers.recall_workbook import inspect_recall
        topics = [{"id": "existing", "subject_code": "MAS", "code": "MAS-1", "title": "Working Capital"}]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "source.xlsx"
            self.source(path)
            result = inspect_recall(path, topics)
        self.assertEqual(len(result["mappings"]), 2)
        self.assertEqual([row["locator"] for row in result["mappings"]], ["MS Recall!A3", "MS Recall!A6"])
        self.assertEqual([row["code"] for row in result["mappings"]], ["MAS-1", "MAS-1"])
        self.assertEqual([row["locator"] for row in result["conflicts"]], ["MS Recall!A4", "MS Recall!A5"])
        self.assertEqual(result["sheets"][0]["duplicate_titles"], 1)

    def test_ambiguous_existing_title_blocks_proposed_mapping(self):
        from app.parsers.recall_workbook import inspect_recall
        topics = [{"subject_code": "MAS", "code": "MAS-1", "title": "Working Capital"},
                  {"subject_code": "MAS", "code": "MAS-2", "title": " Working  Capital "}]
        with TemporaryDirectory() as directory:
            path = Path(directory) / "source.xlsx"
            self.source(path)
            result = inspect_recall(path, topics)
        self.assertEqual(result["mappings"], [])
        self.assertEqual(len(result["conflicts"]), 4)
        self.assertIn("ambiguous", result["conflicts"][0]["reason"])

    def test_report_contains_structure_and_locators_but_never_private_values(self):
        from app.parsers.recall_workbook import inspect_recall
        from app.services.recall_inspect import report
        with TemporaryDirectory() as directory:
            path = Path(directory) / "source.xlsx"
            self.source(path)
            original = path.read_bytes()
            result = inspect_recall(path, [{"id": "PRIVATE_TOPIC_UUID", "subject_code": "MAS", "code": "MAS-1", "title": "Working Capital"}])
            text = report(result)
            self.assertEqual(path.read_bytes(), original)
        for private in ("2035", "98765", "private rating", "SECRET_PRIVATE_FORMULA", "PRIVATE_REMINDER_91", "private formula title", "PRIVATE_TOPIC_UUID"):
            self.assertNotIn(private, text)
            self.assertNotIn(private, str(result))
        self.assertIn("MS Recall!A3", text)
        self.assertIn("MAS-1", text)
        self.assertIn("0", text)
        self.assertEqual(result["sheets"][0]["column_types"]["M"]["formula"], 1)
        self.assertEqual(result["sheets"][0]["column_types"]["B"]["date/time"], 1)


if __name__ == "__main__":
    unittest.main()
