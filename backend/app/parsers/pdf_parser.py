"""Bounded selectable-text extraction. Failed PDFs retain their original only."""
from dataclasses import dataclass, field
from io import BytesIO
import logging

from pypdf import PdfReader, apply_configuration
from pypdf.generic import ContentStream

MAX_PAGES = 200
MAX_PAGE_CHARS = 20_000
MAX_TEXT_CHARS = 1_000_000
MAX_STREAM_BYTES = 2_000_000
MAX_TOTAL_STREAM_BYTES = 20_000_000

# pypdf parser warnings can contain uploaded bytes. Suppress this library's
# warnings consistently, including simultaneous uploads; never toggle per call.
logging.getLogger("pypdf").setLevel(logging.CRITICAL + 1)


@dataclass
class PdfContent:
    processing_status: str
    page_count: int | None = None
    sections: list[dict] = field(default_factory=list)
    error_message: str | None = None


class _ContentLimit(Exception):
    pass


def _check_content(stream, resources, reader, budget, active, depth=0):
    if stream is None:
        return
    identity = id(stream)
    if depth > 30 or identity in active:
        raise _ContentLimit()
    decoded = stream.get_data()
    budget["bytes"] += len(decoded)
    if len(decoded) > MAX_STREAM_BYTES or budget["bytes"] > MAX_TOTAL_STREAM_BYTES:
        raise _ContentLimit()
    active.add(identity)
    try:
        instructions = stream if isinstance(stream, ContentStream) else ContentStream(stream, reader)
        for operands, operator in instructions.operations:
            if operator != b"Do":
                continue
            if not operands:
                raise _ContentLimit()
            target = resources.get("/XObject", {}).get(operands[0])
            if target is None:
                raise _ContentLimit()
            target = target.get_object()
            if target.get("/Subtype") == "/Image":
                continue  # No image extraction/OCR in this phase.
            budget["forms"] += 1
            if budget["forms"] > 200 or target.get("/Subtype") != "/Form":
                raise _ContentLimit()
            _check_content(target, target.get("/Resources", resources), reader, budget, active, depth + 1)
    finally:
        active.remove(identity)


def parse_pdf(data: bytes) -> PdfContent:
    with apply_configuration(maximum_declared_stream_length=MAX_STREAM_BYTES,
            array_based_stream_maximum_output_length=MAX_STREAM_BYTES,
            zlib_maximum_output_length=MAX_STREAM_BYTES, lzw_maximum_output_length=MAX_STREAM_BYTES,
            run_length_maximum_output_length=MAX_STREAM_BYTES, zlib_maximum_recovery_input_length=100_000,
            page_tree_maximum_entries=400, page_tree_maximum_depth=30,
            xform_maximum_invocations_per_extraction=200, jbig2dec_binary=None):
        return _extract(data)


def _extract(data: bytes) -> PdfContent:
    count = None
    try:
        reader = PdfReader(BytesIO(data), strict=True)
        if reader.is_encrypted:
            return PdfContent("failed", error_message="Password-protected PDFs cannot be processed.")
        count = len(reader.pages)
        if not count or count > MAX_PAGES:
            return PdfContent("failed", count or None, error_message="PDF processing supports 1 to 200 pages.")
        sections = []
        total = 0
        budget = {"bytes": 0, "forms": 0}
        for index, page in enumerate(reader.pages):
            # Include repeated/nested Form invocations so extraction cannot silently
            # skip forms or decode content outside the cumulative processing budget.
            contents = page.get_contents()
            budget["forms"] = 0
            _check_content(contents, page.get("/Resources", {}), reader, budget, set())
            content = (page.extract_text() or "").replace("\x00", "").strip()
            total += len(content)
            if len(content) > MAX_PAGE_CHARS or total > MAX_TEXT_CHARS:
                return PdfContent("failed", count, error_message="PDF extracted text exceeds the processing limit.")
            sections.append({"page_number": index + 1, "section_index": index, "content": content})
        if not total:
            return PdfContent("failed", count, error_message="No selectable text was found. OCR is not supported.")
        return PdfContent("ready", count, sections)
    except _ContentLimit:
        return PdfContent("failed", count or None, error_message="PDF page content exceeds the processing limit.")
    except Exception:
        # Parser/provider exception text can contain bytes or private metadata.
        return PdfContent("failed", count, error_message="PDF text extraction failed. The original file is available.")
