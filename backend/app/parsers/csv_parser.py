"""General CSV validation/preview only; never import domain or progress records."""
import csv
from dataclasses import dataclass
from io import StringIO

from app.services.resource_errors import MAX_FILE_BYTES, ResourceError

MAX_COLUMNS = 100
MAX_ROWS = 100_000
MAX_CELL_CHARS = 10_000
MAX_PREVIEW_ROWS = 20


def _validate_quotes(source: str) -> None:
    # csv.reader(strict=True) still accepts quotes embedded in unquoted cells.
    # Validate comma-separated quoting without changing any source values.
    state = "start"
    line = 1
    for index, char in enumerate(source):
        if state == "quoted":
            if char == '"':
                state = "closed"
        elif state == "closed":
            if char == '"':
                state = "quoted"  # doubled quote within the quoted field
            elif char in ",\r\n":
                state = "start"
            else:
                raise ResourceError(422, f"Invalid CSV quoting or field size at row {line}.")
        elif char == '"':
            if state != "start":
                raise ResourceError(422, f"Invalid CSV quoting or field size at row {line}.")
            state = "quoted"
        elif char in ",\r\n":
            state = "start"
        else:
            state = "plain"
        if char == "\n" or (char == "\r" and (index + 1 == len(source) or source[index + 1] != "\n")):
            line += 1
    if state == "quoted":
        raise ResourceError(422, f"Invalid CSV quoting or field size at row {line}.")
MAX_PREVIEW_CHARS = 200_000


@dataclass
class CsvContent:
    headers: list[str]
    rows: list[list[str]]
    row_count: int


def parse_csv(data: bytes) -> CsvContent:
    if not data or len(data) > MAX_FILE_BYTES:
        raise ResourceError(422, "CSV must contain a header and data rows within the file limit.")
    try:
        source = data.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        raise ResourceError(422, "CSV must use UTF-8 encoding.") from None
    if any(ord(char) < 32 and char not in "\r\n\t" for char in source):
        raise ResourceError(422, "CSV contains unsupported control characters.")
    _validate_quotes(source)
    # The standard library owns cell decoding and row boundaries.
    reader = csv.reader(StringIO(source, newline=""), strict=True)
    try:
        headers = next(reader, None)
        if not headers or len(headers) > MAX_COLUMNS or any(not value.strip() or len(value) > 200 for value in headers):
            raise ResourceError(422, "CSV requires nonempty headers, at most 100 columns and 200 characters per header.")
        if len({value.strip().casefold() for value in headers}) != len(headers):
            raise ResourceError(422, "CSV headers must be unique.")
        rows = []
        count = 0
        preview_chars = sum(len(value) for value in headers)
        for row in reader:
            # Empty records are malformed rather than silently changing row counts.
            if len(row) != len(headers):
                raise ResourceError(422, f"Invalid CSV at row {reader.line_num}: expected {len(headers)} columns.")
            if any(len(value) > MAX_CELL_CHARS for value in row):
                raise ResourceError(422, f"Invalid CSV at row {reader.line_num}: a cell exceeds 10000 characters.")
            count += 1
            if count > MAX_ROWS:
                raise ResourceError(422, "CSV exceeds the 100000 data row limit.")
            if len(rows) < MAX_PREVIEW_ROWS:
                preview_chars += sum(len(value) for value in row)
                if preview_chars > MAX_PREVIEW_CHARS:
                    raise ResourceError(422, "CSV preview exceeds the 200000 character limit.")
                rows.append(row)
    except csv.Error:
        raise ResourceError(422, f"Invalid CSV quoting or field size at row {reader.line_num}.") from None
    if not count:
        raise ResourceError(422, "CSV must contain at least one data row.")
    return CsvContent(headers, rows, count)
