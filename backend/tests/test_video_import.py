"""Focused video duration and duplicate-safe planning checks; no live writes."""
import unittest
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from app.parsers.video_workbook import duration_seconds, parse_video_workbook
from app.services.video_import import make_plan
from app.services.curriculum_import import make_plan as topic_plan
from app.parsers.curriculum_workbook import SUBJECT_SHEETS


class VideoImportChecks(unittest.TestCase):
    def test_confirmed_time_formats_and_source_corrections(self):
        def row(value, fmt, sheet="MS Vids", number=3, kind="n"):
            return {"sheet": sheet, "row": number, "duration_format": fmt,
                    "duration_raw_xml_value": str(value), "duration_raw_xml_type": kind,
                    "duration_source": str(value)}
        self.assertEqual(duration_seconds(row(Decimal(79320) / 86400, "h:mm")), 1322)
        self.assertEqual(duration_seconds(row("2.39375", "[h]:mm:ss")), 3447)
        self.assertEqual(duration_seconds(row(Decimal(3654) / 86400, "h:mm:ss")), 3654)
        self.assertEqual(duration_seconds(row("23.59", "General", "FAR Vids", 294)), 1439)
        self.assertEqual(duration_seconds(row("24.46", "General", "FAR Vids", 295)), 1486)
        self.assertEqual(duration_seconds(row("ignored-index", "General", "TAX Vids", 64, "s") | {"duration_source": "27:08:"}), 1628)
        for bad in (row("23.59", "General", number=8), row("-1", "h:mm"),
                    row(Decimal(79321) / 86400, "h:mm"), row("99", "General", "FAR Vids", 294)):
            with self.assertRaises(ValueError):
                duration_seconds(bad)

    def test_real_source_exclusions_mapping_idempotency_and_conflicts(self):
        parsed = parse_video_workbook(Path("../data/imports/Project 1.xlsx"))
        subjects = [{"id": UUID(int=i + 1), "code": code, "is_active": True}
                    for i, code in enumerate(SUBJECT_SHEETS.values())]
        topics = topic_plan(parsed.curriculum, subjects, [])["inserts"]
        plan = make_plan(parsed, subjects, topics, [])
        self.assertFalse(plan["errors"])
        self.assertEqual(len(plan["inserts"]), 1562)
        self.assertEqual({r["row"] for r in parsed.excluded}, {586, 587})
        self.assertEqual(sum(r["reason"].startswith("formula-only") for r in parsed.skipped), 7)
        self.assertTrue(all(r["duration_seconds"] > 0 for r in plan["inserts"]))
        again = make_plan(parsed, subjects, topics, plan["inserts"])
        self.assertEqual(again["inserts"], [])
        self.assertEqual(again["unchanged"], 1562)
        self.assertFalse(again["errors"])
        changed = deepcopy(plan["inserts"])
        changed[0]["duration_seconds"] += 1
        self.assertTrue(make_plan(parsed, subjects, topics, changed)["errors"])
        self.assertTrue(make_plan(parsed, subjects, topics[:-1], [])["errors"])
        self.assertTrue(make_plan(parsed, subjects, topics, plan["inserts"] + [plan["inserts"][0]])["errors"])
        duplicate_alias = deepcopy(parsed)
        source = next(r for r in parsed.videos if r["code"] == "RFBT-11A")
        duplicate_alias.videos.append({**source, "code": "RFBT-11a", "row": 999,
                                       "source_code": "project-1:RFBT Vids:999"})
        self.assertTrue(make_plan(duplicate_alias, subjects, topics, [])["errors"])


if __name__ == "__main__":
    unittest.main()
