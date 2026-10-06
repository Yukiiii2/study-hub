"""Literal, source-traceable Project 1 curriculum extraction. Never evaluates formulas."""
from collections import Counter
from dataclasses import dataclass, field
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re
from posixpath import normpath
from zipfile import ZipFile
from xml.etree import ElementTree

from openpyxl import load_workbook

SUBJECT_SHEETS = {"MS": "MAS", "AT": "AT", "AP": "AP", "RFBT": "RFBT", "TAX": "TAX", "FAR": "FAR", "AFAR": "AFAR"}
MAPPING = {
    "subject_sheets": SUBJECT_SHEETS, "header_row": 2, "first_topic_row": 4,
    "code_column": "B", "title_column": "C", "hierarchy": "flat",
    "description": None, "display_order": "source row number",
    "identity": "subject UUID + exact whitespace-normalized source code",
}


def normalize(value: str) -> str:
    return " ".join(value.split())


def literal(cell) -> str | None:
    if cell.data_type in ("f", "e") or not isinstance(cell.value, str):
        return None
    return normalize(cell.value) or None


@dataclass
class ParsedWorkbook:
    filename: str
    digest: str
    topics: list[dict] = field(default_factory=list)
    inventory: list[dict] = field(default_factory=list)
    candidates: Counter = field(default_factory=Counter)
    skipped: list[dict] = field(default_factory=list)
    ambiguous: list[dict] = field(default_factory=list)
    duplicates: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    deferred: dict = field(default_factory=dict)


def parse_workbook(path: Path) -> ParsedWorkbook:
    # Hash exactly the bytes parsed, so an edited source cannot pass an old approval.
    data = path.read_bytes()
    result = ParsedWorkbook(path.name, sha256(data).hexdigest())
    book = load_workbook(BytesIO(data), data_only=False, keep_links=False)
    try:
        for sheet in book:
            result.inventory.append({"sheet": sheet.title, "extent": sheet.calculate_dimension(),
                                     "formulas": sum(c.data_type == "f" for row in sheet for c in row),
                                     "merges": [str(r) for r in sheet.merged_cells.ranges]})
        for sheet_name, subject in SUBJECT_SHEETS.items():
            if sheet_name not in book.sheetnames:
                result.errors.append(f"Missing subject sheet: {sheet_name}")
                continue
            sheet = book[sheet_name]
            if literal(sheet["B2"]) != "HO#" or literal(sheet["C2"]) != "Sub-topics":
                result.errors.append(f"Unexpected curriculum headers: {sheet_name}!B2:C2")
                continue
            seen = set()
            for row in range(1, sheet.max_row + 1):
                code_cell, title_cell = sheet[f"B{row}"], sheet[f"C{row}"]
                code, title = literal(code_cell), literal(title_cell)
                trace = {"sheet": sheet_name, "row": row, "subject": subject, "code": code}
                if row < 4:
                    result.skipped.append({**trace, "reason": "header/label"})
                    continue
                if code_cell.value is not None or title_cell.value is not None:
                    result.candidates[subject] += 1
                if code_cell.data_type in ("f", "e") or title_cell.data_type in ("f", "e"):
                    result.errors.append(f"Formula/error in curriculum fields: {sheet_name}!B{row}:C{row}")
                    result.skipped.append({**trace, "reason": "formula/error"})
                    continue
                if code is None and title is None:
                    result.skipped.append({**trace, "reason": "blank curriculum fields"})
                    continue
                if code and title is None and title_cell.value in (None, ""):
                    result.ambiguous.append({**trace, "reason": "code without usable title"})
                    result.skipped.append({**trace, "reason": "code without usable title"})
                    continue
                if not code or not title or not re.fullmatch(subject + r"-\d+(?:\.\d+|[A-Za-z])?", code):
                    result.errors.append(f"Invalid literal curriculum code/title: {sheet_name}!B{row}:C{row}")
                    continue
                if code.casefold() in seen:
                    result.duplicates.append(trace)
                    result.errors.append(f"Duplicate source code: {sheet_name}!B{row} ({code})")
                    continue
                seen.add(code.casefold())
                result.topics.append({**trace, "title": title, "description": None,
                                      "parent_topic_id": None, "display_order": row})
            mirror_name = sheet_name + " Code"
            if mirror_name not in book.sheetnames:
                result.errors.append(f"Missing corroborating Code sheet: {mirror_name}")
                continue
            mirror = book[mirror_name]
            if literal(mirror["A2"]) != "CODE" or literal(mirror["B2"]) != "TOPIC":
                result.errors.append(f"Unexpected Code headers: {mirror_name}")
                continue
            mirror_rows = {}
            for row in range(3, mirror.max_row + 1):
                code, title = literal(mirror[f"A{row}"]), literal(mirror[f"B{row}"])
                if code and title:
                    if code in mirror_rows:
                        result.errors.append(f"Duplicate corroborating code: {mirror_name}!A{row}")
                    mirror_rows[code] = title
            for topic in [t for t in result.topics if t["subject"] == subject]:
                if mirror_rows.get(topic["code"]) != topic["title"]:
                    result.errors.append(f"Code-sheet mismatch for {subject}/{topic['code']}")
            if literal(mirror["A1"]) not in (subject, sheet_name, None):
                result.warnings.append(f"{mirror_name}!A1 has a misleading heading; explicit sheet/code mapping is used.")
        for row in result.ambiguous:
            result.warnings.append(f"Excluded {row['sheet']}!B{row['row']} ({row['code']}): missing title.")
        result.warnings.append("No explicit parent links or title indentation: all curriculum topics remain flat, including dotted/letter-suffixed codes.")
        result.deferred = inspect_deferred(book, result, raw_duration_cells(data))
    finally:
        book.close()
    return result


def raw_duration_cells(data: bytes) -> dict:
    """Preserve original numeric XML values before the reader converts Excel time types."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    result = {}
    with ZipFile(BytesIO(data)) as archive:
        relationships = {r.get("Id"): normpath("xl/" + r.get("Target")).lstrip("/")
                         if not r.get("Target").startswith("/") else r.get("Target").lstrip("/")
                         for r in ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        sheets = ElementTree.fromstring(archive.read("xl/workbook.xml")).find("s:sheets", ns)
        for sheet in sheets:
            if not sheet.get("name").endswith(" Vids"):
                continue
            relationship = sheet.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            document = ElementTree.fromstring(archive.read(relationships[relationship]))
            for cell in document.findall(".//s:c", ns):
                if re.fullmatch(r"C\d+", cell.get("r", "")):
                    value = cell.find("s:v", ns)
                    result[(sheet.get("name"), cell.get("r"))] = {
                        "duration_raw_xml_value": value.text if value is not None else None,
                        "duration_raw_xml_type": cell.get("t", "n"),
                    }
    return result


def inspect_deferred(book, parsed: ParsedWorkbook, raw_durations: dict) -> dict:
    """Safe curriculum-only auxiliary plans: omit personal progress/history/remarks."""
    videos, recall = [], []
    for sheet_name, subject in SUBJECT_SHEETS.items():
        topics = [t for t in parsed.topics if t["subject"] == subject]
        codes = {t["code"] for t in topics}
        titles = {t["title"] for t in topics}
        for suffix in (" Vids", " Recall"):
            name = sheet_name + suffix
            if name not in book.sheetnames:
                parsed.warnings.append(f"Missing deferred source sheet: {name}")
                continue
            sheet = book[name]
            for row in range(2 if suffix == " Vids" else 3, sheet.max_row + 1):
                if suffix == " Vids":
                    code, title = literal(sheet[f"A{row}"]), literal(sheet[f"B{row}"])
                    if not code or not title:
                        continue
                    cell = sheet[f"C{row}"]
                    # openpyxl converts Excel times; repr retains type and format rather than guessing seconds.
                    valid = cell.data_type not in ("f", "e") and cell.value is not None and not isinstance(cell.value, (str, bool))
                    if isinstance(cell.value, (int, float)) and cell.value < 0:
                        valid = False
                    videos.append({"sheet": name, "row": row, "subject": subject, "code": code,
                                   "title": title, "exact_topic_match": code in codes,
                                   "duration_source": str(cell.value), "duration_type": type(cell.value).__name__,
                                   "duration_format": cell.number_format, "duration_valid_literal": valid,
                                   **raw_durations.get((name, cell.coordinate), {})})
                else:
                    title = literal(sheet[f"A{row}"])
                    if title:
                        recall.append({"sheet": name, "row": row, "subject": subject,
                                       "title": title, "exact_topic_match": title in titles})
    assessments = []
    if "ASSESSMENTS" in book.sheetnames:
        sheet = book["ASSESSMENTS"]
        columns = {"B": "FAR", "D": "AFAR", "F": "MAS", "H": "TAX", "J": "RFBT", "L": "AT", "N": "AP"}
        section = None
        section_rows = {r.min_row for r in sheet.merged_cells.ranges if r.min_col == 1 and r.max_col == 14}
        for row in range(2, sheet.max_row + 1):
            if row in section_rows:
                section = literal(sheet[f"A{row}"])
                continue
            for column, subject in columns.items():
                title = literal(sheet[f"{column}{row}"])
                if title and section:
                    matches = [t["code"] for t in parsed.topics if t["subject"] == subject and t["title"] == title]
                    assessments.append({"section": section, "subject": subject, "coverage": title,
                                        "cell": f"{column}{row}", "exact_topic_code": matches[0] if len(matches) == 1 else None})
    return {"videos": videos, "recall": recall, "assessments": assessments,
            "schedule": {"sheet": "SCHEDULE", "subject_row": 4, "weekday_row": 5,
                         "columns": {"C": "RFBT", "F": "AFAR", "I": "AT/AUD (unresolved)", "L": "MAS", "O": "TAX", "R": "FAR", "U": "recall/backlogs/rest"}},
            "calendar": {"sheet": "Calendar", "strategy": "Month-header/date-grid context required; no personal event notes copied"}}
