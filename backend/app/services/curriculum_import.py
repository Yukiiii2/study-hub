"""Dry-run-first, insert-only CLI for the reviewed Project 1 curriculum mapping."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import text

from app.db.connection import get_engine
from app.parsers.curriculum_workbook import MAPPING, SUBJECT_SHEETS, ParsedWorkbook, normalize, parse_workbook

ROOT = Path(__file__).resolve().parents[3]


def fingerprint(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, default=str, ensure_ascii=False).encode()).hexdigest()


def validate_integrity(rows: list[dict]) -> list[str]:
    errors = []
    by_id = {str(row["id"]): row for row in rows}
    codes = set()
    for row in rows:
        subject = str(row["subject_id"])
        if row["code"]:
            key = (subject, normalize(row["code"]).casefold())
            if key in codes:
                errors.append(f"Duplicate database topic code: {row['code']}")
            codes.add(key)
        parent = row["parent_topic_id"]
        if parent is not None:
            owner = by_id.get(str(parent))
            if owner is None or str(owner["subject_id"]) != subject:
                errors.append(f"Orphan/cross-subject parent on topic {row['id']}")
        visited = {str(row["id"])}
        while parent is not None and str(parent) in by_id:
            if str(parent) in visited:
                errors.append(f"Cycle at topic {row['id']}")
                break
            visited.add(str(parent))
            parent = by_id[str(parent)]["parent_topic_id"]
    return errors


def make_plan(parsed: ParsedWorkbook, subjects: list[dict], existing: list[dict]) -> dict:
    errors = list(parsed.errors) + validate_integrity(existing)
    subject_map = {row["code"]: row for row in subjects}
    for code in SUBJECT_SHEETS.values():
        if code not in subject_map or not subject_map[code]["is_active"]:
            errors.append(f"Missing/inactive existing subject: {code}")
    by_code = defaultdict(list)
    for row in existing:
        if row["code"]:
            by_code[(str(row["subject_id"]), normalize(row["code"]).casefold())].append(row)
    inserts, unchanged = [], 0
    ids = {str(row["id"]) for row in existing}
    for topic in parsed.topics:
        subject = subject_map.get(topic["subject"])
        if subject is None:
            continue
        subject_id = str(subject["id"])
        expected = {"id": str(uuid5(NAMESPACE_URL, f"study-hub/project-1/curriculum/v1/{subject_id}/{topic['code']}")),
                    "subject_id": subject_id, "parent_topic_id": None, "code": topic["code"],
                    "title": topic["title"], "description": None, "display_order": topic["display_order"]}
        matches = by_code[(subject_id, topic["code"].casefold())]
        if len(matches) > 1:
            errors.append(f"Multiple existing records match {topic['subject']}/{topic['code']}")
        elif matches:
            actual = matches[0]
            if any(actual[field] != expected[field] for field in ("code", "title", "description", "parent_topic_id", "display_order")):
                errors.append(f"Existing record conflict for {topic['subject']}/{topic['code']}; no overwrite allowed")
            else:
                unchanged += 1
        elif expected["id"] in ids:
            errors.append(f"Deterministic identity collision for {topic['subject']}/{topic['code']}")
        else:
            inserts.append(expected)
    plan = {"version": 1, "workbook_sha256": parsed.digest, "mapping": MAPPING,
            "database_snapshot": fingerprint({"subjects": subjects, "topics": existing}),
            "inserts": inserts, "updates": 0, "unchanged": unchanged, "errors": errors}
    plan["fingerprint"] = fingerprint(plan)
    return plan


def read_state(connection) -> tuple[list[dict], list[dict]]:
    subjects = [dict(row) for row in connection.execute(text(
        "SELECT id, code, is_active FROM public.subjects ORDER BY code"
    )).mappings()]
    topics = [dict(row) for row in connection.execute(text(
        "SELECT id, subject_id, parent_topic_id, code, title, description, display_order "
        "FROM public.topics ORDER BY id"
    )).mappings()]
    return subjects, topics


def migrate(parsed: ParsedWorkbook, approved: dict) -> dict:
    if approved.get("errors") or not approved.get("fingerprint"):
        raise ValueError("A successful dry-run plan is required")
    with get_engine().begin() as connection:
        connection.execute(text("SET LOCAL lock_timeout = '10s'"))
        connection.execute(text("LOCK TABLE public.subjects IN SHARE MODE"))
        connection.execute(text("LOCK TABLE public.topics IN SHARE ROW EXCLUSIVE MODE"))
        subjects, before = read_state(connection)
        plan = make_plan(parsed, subjects, before)
        if plan["errors"] or plan["fingerprint"] != approved["fingerprint"]:
            raise ValueError("Source/database/mapping changed or conflicts remain; run and review a new dry run")
        if plan["inserts"]:
            connection.execute(text(
                "INSERT INTO public.topics(id, subject_id, parent_topic_id, code, title, description, display_order) "
                "VALUES (:id, :subject_id, :parent_topic_id, :code, :title, :description, :display_order)"
            ), plan["inserts"])
        subjects, after = read_state(connection)
        verification = make_plan(parsed, subjects, after)
        if verification["errors"] or verification["inserts"] or verification["unchanged"] != len(parsed.topics):
            raise ValueError("Post-insert validation failed; transaction rolled back")
        if len(after) != len(before) + len(plan["inserts"]):
            raise ValueError("Unexpected topic count change; transaction rolled back")
        return {**plan, "inserted": len(plan["inserts"]), "verified": len(parsed.topics),
                "database_counts": dict(Counter(str(row["subject_id"]) for row in after))}


def write_report(parsed: ParsedWorkbook, plan: dict, path: Path, committed: bool = False) -> None:
    def safe(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["# Project 1 curriculum migration " + ("result" if committed else "dry run"), "",
             f"Workbook: `{parsed.filename}`; SHA-256: `{parsed.digest}`.", "",
             "Mode: " + ("transactional insert; post-write validation passed" if committed else "read-only; no database records written"), "",
             f"Proposed inserts: {len(plan['inserts'])}; updates: 0; unchanged: {plan['unchanged']}; critical errors: {len(plan['errors'])}."]
    if committed:
        lines += [f"Inserted: {plan['inserted']}; matching topics verified: {plan['verified']}."]
    lines += ["", "## Sheets detected", "", "| Sheet | Stored extent | Formula cells | Merges |", "| --- | --- | ---: | ---: |"]
    for item in parsed.inventory:
        lines.append(f"| {safe(item['sheet'])} | {item['extent']} | {item['formulas']} | {len(item['merges'])} |")
    lines += ["", "Stored extents include formatting-only cells. Formula values/errors are never curriculum input. Header merges are not hierarchy evidence.", "",
              "## Subject mapping and counts", "", "| Sheet | Subject | Candidates | Accepted | Skipped |", "| --- | --- | ---: | ---: | ---: |"]
    for sheet, code in SUBJECT_SHEETS.items():
        lines.append(f"| {sheet} | {code} | {parsed.candidates[code]} | {sum(t['subject'] == code for t in parsed.topics)} | {sum(t['subject'] == code for t in parsed.skipped)} |")
    lines += ["", "## Rules", "", "Literal B/C fields after row 3, verified against Code sheets; whitespace normalization only. Source row number is display_order. No descriptions are inferred from progress checkboxes. All parent_topic_id values are null; dotted/letter suffixes remain flat because explicit relationships are absent.", "",
              "Exact subject + source code identifies a topic. UUIDv5 uses NAMESPACE_URL and study-hub/project-1/curriculum/v1/{subject UUID}/{code}. Existing differences in title, code case/spacing, description, parent, or order block import. No updates, deletes, subject writes, or schema changes. Table locks and a matching source/mapping/database plan fingerprint prevent stale approvals and concurrent duplicate insertion.", "",
              "## Warnings, ambiguities, duplicates, and errors", ""]
    lines += ["- " + safe(item) for item in parsed.warnings + plan["errors"]]
    lines += [f"- Source duplicates: {len(parsed.duplicates)}; incomplete/ambiguous rows: {len(parsed.ambiguous)}.", "", "## Skipped source rows", ""]
    for item in parsed.skipped:
        lines.append(f"- {item['sheet']}!{item['row']}: {item['reason']}" + (f" ({item['code']})" if item['code'] else ""))
    lines += ["", "## Accepted topic traceability", "", "| Subject | Source | Code | Title | Parent |", "| --- | --- | --- | --- | --- |"]
    for t in parsed.topics:
        lines.append(f"| {t['subject']} | {t['sheet']}!B{t['row']}:C{t['row']} | {safe(t['code'])} | {safe(t['title'])} | none |")
    lines += ["", "## Deferred video mapping", "", "No video table exists; zero video writes. A is source topic code, B lecture title, C duration. D (and FAR E/F) contains personal progress and is excluded. Blank-code headers and Total Time rows are not lecture candidates. Duration types/formats are preserved without guessing units or converting to seconds.", "",
              "| Subject | Coded lectures | Exact topic-code matches | Invalid literal durations |", "| --- | ---: | ---: | ---: |"]
    for code in SUBJECT_SHEETS.values():
        rows = [r for r in parsed.deferred["videos"] if r["subject"] == code]
        lines.append(f"| {code} | {len(rows)} | {sum(r['exact_topic_match'] for r in rows)} | {sum(not r['duration_valid_literal'] for r in rows)} |")
    lines.append("")
    for row in parsed.deferred["videos"]:
        if not row["exact_topic_match"] or not row["duration_valid_literal"]:
            lines.append(f"- Review {row['sheet']}!{row['row']}: topic code {row['code']}; exact match {row['exact_topic_match']}; literal duration valid {row['duration_valid_literal']}.")
    lines += ["", "## Deferred recall mapping", "", "A topic; B First Rep; C/D through K/L alternate R1–R5 and ratings; M Next Rep; N Final Rating; O Remarks. Numeric repetition values and formulas do not establish an algorithm. Personal history/ratings/remarks are not copied. Exact whitespace-normalized title matching only.", "",
              "| Subject | References | Exact title matches |", "| --- | ---: | ---: |"]
    for code in SUBJECT_SHEETS.values():
        rows = [r for r in parsed.deferred["recall"] if r["subject"] == code]
        lines.append(f"| {code} | {len(rows)} | {sum(r['exact_topic_match'] for r in rows)} |")
    lines.append("")
    for row in parsed.deferred["recall"]:
        if not row["exact_topic_match"]:
            lines.append(f"- Unresolved title: {row['sheet']}!A{row['row']}.")
    lines += ["", "## Deferred schedule and calendar mapping", "",
              "SCHEDULE row 4 subject / row 5 weekday columns: C RFBT, F AFAR, I AT/AUD, L MAS, O TAX, R FAR, U recall/backlogs/rest. I cannot be split between AT and AP without review. Date rows, helpers, literal tasks, and formula labels require separate mapping; formulas are not event titles. Calendar needs month-header plus day-grid context. Private dates/reminders/events are not copied into this safe report. No schedule/calendar tables or writes.", "",
              "## Deferred assessments", "", "Merged section labels supply names; row 1 columns B/D/F/H/J/L/N map FAR/AFAR/MAS/TAX/RFBT/AT/AP. Adjacent helper/progress columns are excluded. No assessment dates or coverage relationships are invented. No assessment table or writes.", "",
              "| Section | Literal coverage entries | Exact unique topic matches |", "| --- | ---: | ---: |"]
    sections = sorted({r["section"] for r in parsed.deferred["assessments"]})
    for section in sections:
        rows = [r for r in parsed.deferred["assessments"] if r["section"] == section]
        lines.append(f"| {safe(section)} | {len(rows)} | {sum(r['exact_topic_code'] is not None for r in rows)} |")
    lines += ["", "Normalized curriculum-only auxiliary candidates (video titles/duration representations, recall topic references, and assessment coverage cells) are in the adjacent .source-plan.json file. Personal progress/history/events/remarks and credentials are excluded. The personal workbook remains local and ignored.", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    path.with_suffix(".plan.json").write_text(json.dumps(plan, indent=2, default=str, ensure_ascii=False) + "\n", encoding="utf-8")
    path.with_suffix(".source-plan.json").write_text(json.dumps(parsed.deferred, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "data/imports/Project 1.xlsx")
    parser.add_argument("--report", type=Path, default=ROOT / "data/imports/reports/project-1-dry-run.md")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--approved-plan", type=Path)
    args = parser.parse_args()
    if args.commit and (not args.approved_plan or args.report.with_suffix(".plan.json").resolve() == args.approved_plan.resolve()):
        parser.error("--commit requires --approved-plan and a separate --report path")
    committed = False
    try:
        parsed = parse_workbook(args.workbook)
        if args.commit:
            approved = json.loads(args.approved_plan.read_text(encoding="utf-8"))
            plan = migrate(parsed, approved)
            committed = True
        else:
            with get_engine().begin() as connection:
                connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
                subjects, topics = read_state(connection)
                plan = make_plan(parsed, subjects, topics)
        write_report(parsed, plan, args.report, args.commit)
        print(f"Accepted {len(parsed.topics)}; inserts {len(plan['inserts'])}; updates 0; unchanged {plan['unchanged']}; errors {len(plan['errors'])}.")
        print("Report:", args.report)
        return 1 if plan["errors"] else 0
    except Exception as error:
        # Never print raw driver/provider exceptions, connection strings, or credentials.
        if committed:
            print(f"Database import committed and verified, but report generation failed ({type(error).__name__}). Run a fresh dry run for the current state.")
        else:
            print(f"Migration stopped ({type(error).__name__}); no partial transaction is committed. Review setup and the dry-run report.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
