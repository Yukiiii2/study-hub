"""Bounded, literal question CSV decoding; never writes or infers associations."""
import csv
from dataclasses import dataclass, field
from io import StringIO

from app.parsers.csv_parser import _validate_quotes
from app.services.resource_errors import ResourceError

MAX_FILE_BYTES = 1024 * 1024
MAX_ROWS = 500
HEADERS = ("subject", "topic", "question_type", "question", "option_a", "option_b",
           "option_c", "option_d", "option_e", "option_f", "correct_answer",
           "explanation", "resource_id", "source_page")


class QuizImportError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


@dataclass
class QuizCsv:
    rows: list[tuple[int, dict[str, str]]] = field(default_factory=list)
    row_count: int = 0
    errors: list[dict] = field(default_factory=list)


def issue(row, field, message):
    return {"row": row, "field": field, "message": message}


def parse_quiz_csv(data: bytes) -> QuizCsv:
    if len(data) > MAX_FILE_BYTES:
        raise QuizImportError(413, "Question CSV files must be 1 MiB or smaller.")
    result = QuizCsv()
    if data.startswith((b"%PDF-", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\x89PNG")):
        result.errors.append(issue(1, "file", "CSV contains unsupported binary content."))
        return result
    try:
        source = data.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        result.errors.append(issue(1, "file", "CSV must use UTF-8 encoding."))
        return result
    if any(ord(char) < 32 and char not in "\r\n\t" for char in source):
        result.errors.append(issue(1, "file", "CSV contains unsupported control characters."))
        return result
    try:
        _validate_quotes(source)
    except ResourceError:
        result.errors.append(issue(1, "file", "CSV contains invalid quoting."))
        return result
    reader = csv.reader(StringIO(source, newline=""), strict=True)
    try:
        headers = next(reader, [])
        if (not headers or len(set(headers)) != len(headers) or
                any(header not in HEADERS for header in headers) or
                not {"question", "correct_answer"}.issubset(headers)):
            result.errors.append(issue(1, "headers", "Use unique supported comma-separated headers including question and correct_answer."))
            return result
        for values in reader:
            row_number = result.row_count + 2
            result.row_count += 1
            if result.row_count > MAX_ROWS:
                result.errors.append(issue(row_number, "file", "CSV exceeds the 500 data row limit."))
                break
            if len(values) != len(headers):
                result.errors.append(issue(row_number, "row", "CSV row does not match the header column count."))
                continue
            if any(len(value) > 10_000 for value in values):
                result.errors.append(issue(row_number, "row", "A CSV cell exceeds the 10000 character limit."))
                continue
            result.rows.append((row_number, dict(zip(headers, values))))
    except csv.Error:
        result.errors.append(issue(result.row_count + 2, "file", "CSV contains invalid quoting or field size."))
    if result.row_count == 0 and not result.errors:
        result.errors.append(issue(2, "file", "CSV must contain at least one question row."))
    return result
