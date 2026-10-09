"""Read-only Recall topic-map proposal; no card/review import or commit mode."""
import argparse
from pathlib import Path

from sqlalchemy import text

from app.db.connection import get_engine
from app.parsers.recall_workbook import COLUMN_ROLES, inspect_recall

ROOT = Path(__file__).resolve().parents[3]
TYPE_NAMES = ("blank", "numeric", "date/time", "text", "formula", "boolean", "error", "other")


def read_topics():
    with get_engine().begin() as connection:
        connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        rows = connection.execute(text("SELECT s.code AS subject_code,t.code,t.title FROM public.topics t "
                                       "JOIN public.subjects s ON s.id=t.subject_id WHERE s.is_active "
                                       "ORDER BY s.display_order,t.display_order,t.id")).mappings().all()
        return [dict(row) for row in rows]


def _cell(value):
    return str("—" if value is None or value == "" else value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def report(result):
    mapped = len(result["mappings"])
    references = sum(sheet["source_rows"] for sheet in result["sheets"])
    lines = ["# Project 1 Recall topic mapping proposal", "",
             f"Workbook: `{result['filename']}`; SHA-256 `{result['digest']}`.", "",
             "Read-only workbook inspection and read-only existing curriculum lookup. "
             "Card inserts/updates: **0**; review/history inserts/updates: **0**. "
             "No workbook edits, authenticated-owner assignment, source-history transfer, or commit mode.", "",
             "## Exact mapping rules and counts", "",
             f"Inspected all {len(result['sheets'])} actual `* Recall` worksheets against "
             f"{result['existing_topics']} existing topics under active subjects. "
             f"{mapped} of {references} source references have one exact existing match; "
             f"{len(result['conflicts'])} remain unresolved.", "",
             "Use column A from row 3; map worksheet subject MS to MAS and retain the other approved subject codes. "
             "Normalize whitespace only. Case, punctuation and spelling remain significant. "
             "The subject plus normalized title must identify exactly one existing topic. "
             "No positional, fuzzy, case-insensitive, or cross-subject association is accepted.", "",
             "| Sheet | Subject | Stored range | References | Literal titles | Mapped | Unresolved | Repeated titles |",
             "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for sheet in result["sheets"]:
        lines.append("| " + " | ".join(_cell(sheet[key]) for key in ("sheet", "subject", "extent", "source_rows", "literal_titles", "mapped", "conflicts", "duplicate_titles")) + " |")
    lines += ["", "## Source structure and aggregate cell types", "",
              "A contains topic references. B is First Rep; C/D, E/F, G/H, I/J and K/L alternate R1–R5 with ratings. "
              "M is Next Rep; N is Final Rating; O is Remarks. "
              "Stored worksheet ranges may include formatting-only rows/columns. "
              "Counts below cover body cells from row 3, including blanks; they are cell-type counts, not review counts.", "",
              "| Sheet | Column role | Blank | Numeric | Date/time | Text | Formula | Boolean | Error | Other |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for sheet in result["sheets"]:
        for column, role in COLUMN_ROLES.items():
            counts = sheet["column_types"][column]
            lines.append("| " + " | ".join([_cell(sheet["sheet"]), column + ": " + role, *[str(counts.get(kind, 0)) for kind in TYPE_NAMES]]) + " |")
        if sheet["other_column_types"]:
            counts = sheet["other_column_types"]
            lines.append("| " + " | ".join([_cell(sheet["sheet"]), "Beyond O (aggregate)", *[str(counts.get(kind, 0)) for kind in TYPE_NAMES]]) + " |")
    lines += ["", "Formulas are identified only by stored cell type, never evaluated or printed. "
              "Numeric/date cells and repetition labels do not establish an algorithm, completed reviews, "
              "ratings, actual recall dates or readiness. The application scheduler is defined independently "
              "by the Phase 9 contract; this workbook does not configure it.", "", "## Structural warnings", ""]
    lines += ["- " + _cell(warning) for warning in result["warnings"]] or ["None."]
    lines += ["", "## Unresolved source references", ""]
    lines += [f"- `{_cell(row['locator'])}` ({_cell(row['subject'])}): "
              f"{_cell(row.get('title', 'literal title omitted'))}; {row['reason']}."
              for row in result["conflicts"]] or ["None."]
    lines += ["", "The Phase 4 report flagged `AP Recall!A6`; only an exact current match could resolve it. "
              "Any mismatch remains excluded from the proposal. No source title is corrected and no topic is invented.", "",
              *[f"For source-conflict context, existing curriculum `{_cell(topic['code'])}` is "
                f"`{_cell(topic['title'])}`. This comparison does not create an accepted association."
                for topic in result["phase4_context"]], "",
              "## Accepted source locators and topic codes", "",
              "| Source locator | Subject | Normalized source title | Existing topic code |",
              "| --- | --- | --- | --- |"]
    lines += ["| " + " | ".join(_cell(row[key]) for key in ("locator", "subject", "title", "code")) + " |"
              for row in result["mappings"]]
    lines += ["", "## Phase 9 decision and privacy", "",
              "This is a topic-association proposal only. The Recall sheets do not supply authored front/back pairs. "
              "Do not create cards from topic titles or reinterpret R1–R5 as application reviews. "
              "Users author cards explicitly; new cards follow the separately approved server scheduler. "
              "Resolving a source title mismatch permits a topic reference, not card or history creation.", "",
              "Personal repetition values, ratings, dates, remarks, raw formulas, private UUIDs and credentials "
              "are omitted. The source workbook remains local and ignored. No database writes are supported.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "data/imports/Project 1.xlsx")
    parser.add_argument("--report", type=Path, default=ROOT / "data/imports/reports/project-1-recall-proposal.md")
    args = parser.parse_args()
    if args.report.suffix.lower() != ".md" or args.report.resolve() == args.workbook.resolve():
        parser.error("The proposal report must be a separate Markdown file.")
    try:
        result = inspect_recall(args.workbook, read_topics())
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report(result), encoding="utf-8")
        print(f"Recall proposal: {len(result['sheets'])} sheets; {len(result['mappings'])} mapped references; "
              f"{len(result['conflicts'])} unresolved. Report-only: 0 database writes.")
        return 0
    except Exception as error:
        print(f"Recall inspection stopped ({type(error).__name__}); no database writes were performed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
