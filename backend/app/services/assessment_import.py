"""Read-only-first, owner-explicit and insert-only Project 1 assessment CLI."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import text

from app.db.connection import get_engine
from app.parsers.assessment_workbook import MAPPING, SUBJECT_COLUMNS, ParsedAssessments, parse_assessment_workbook
from app.parsers.curriculum_workbook import normalize
from app.services.curriculum_import import ROOT, fingerprint, read_state

FIELDS = ("title", "description", "scheduled_at", "status", "source_key")


def make_plan(parsed: ParsedAssessments, subjects: list[dict], topics: list[dict], existing: list[dict], user_id: UUID) -> dict:
    """Plan against the explicit owner's definitions, excluding every foreign record."""
    owner = str(UUID(str(user_id)))
    existing = [row for row in existing if str(row["user_id"]) == owner]
    errors = list(parsed.errors)
    subject_map = {}
    for subject in subjects:
        code = subject["code"]
        if code in subject_map:
            errors.append(f"Ambiguous existing subject: {code}")
        subject_map[code] = subject
    for code in SUBJECT_COLUMNS.values():
        if code not in subject_map or not subject_map[code]["is_active"]:
            errors.append(f"Missing/inactive existing subject: {code}")
    titles = defaultdict(list)
    subject_codes = {str(s["id"]): s["code"] for s in subjects if s["is_active"]}
    for topic in topics:
        code = subject_codes.get(str(topic["subject_id"]))
        if code:
            titles[(code, normalize(topic["title"]))].append(topic)
    keyed = defaultdict(list)
    same_titles = defaultdict(list)
    ids = {str(row["id"]) for row in existing}
    for row in existing:
        if row["source_key"]:
            keyed[row["source_key"]].append(row)
        same_titles[normalize(row["title"])].append(row)
    inserts, unchanged, unmapped, superseded, mappings = [], 0, [], [], []
    seen_keys, seen_titles = set(), set()
    for section in parsed.sections:
        key = section["source_key"]
        if key in seen_keys or section["title"] in seen_titles:
            errors.append(f"Duplicate source section identity/title at ASSESSMENTS!A{section['row']}")
            continue
        seen_keys.add(key)
        seen_titles.add(section["title"])
        whole_codes = {r["subject"] for r in section["coverage"] if r["whole_subject"]}
        topic_ids, subject_ids, mapped = [], [], []
        excluded = 0
        for coverage in section["coverage"]:
            code = coverage["subject"]
            subject = subject_map.get(code)
            if subject is None or not subject["is_active"]:
                continue
            if coverage["whole_subject"]:
                if str(subject["id"]) not in subject_ids:
                    subject_ids.append(str(subject["id"]))
                mapped.append({**coverage, "scope": "all_topics", "topic_code": None})
            elif code in whole_codes:
                superseded.append({**coverage, "reason": "explicit whole-subject coverage supersedes individual topic"})
            else:
                matches = titles[(code, coverage["label"])]
                if len(matches) != 1:
                    unmapped.append({**coverage, "reason": "ambiguous exact title" if matches else "no exact subject/title match"})
                    excluded += 1
                    continue
                topic = matches[0]
                if str(topic["id"]) not in topic_ids:
                    topic_ids.append(str(topic["id"]))
                mapped.append({**coverage, "scope": "selected_topic", "topic_code": topic["code"]})
        description = "Imported literal coverage from Project 1 ASSESSMENTS; no source date or result."
        if excluded:
            description += f" Partial coverage: {excluded} source coverage entries excluded because no unique exact subject/topic title match exists."
        expected = {"id": str(uuid5(NAMESPACE_URL, f"study-hub/project-1/assessments/v1/{owner}/{key}")),
                    "user_id": owner, "title": section["title"], "description": description,
                    "scheduled_at": None, "status": "planned", "source_key": key,
                    "topic_ids": topic_ids, "subject_ids": subject_ids}
        candidates = keyed[key]
        collisions = [r for r in same_titles[section["title"]] if r["source_key"] != key]
        if len(candidates) > 1 or collisions:
            errors.append(f"Existing source-key/title collision at {key}; no merge or overwrite")
        elif candidates:
            actual = candidates[0]
            if (any(actual[field] != expected[field] for field in FIELDS)
                    or set(map(str, actual["topic_ids"])) != set(topic_ids)
                    or set(map(str, actual["subject_ids"])) != set(subject_ids)):
                errors.append(f"Existing assessment differs at {key}; no overwrite")
            else:
                unchanged += 1
        elif expected["id"] in ids:
            errors.append(f"Existing identity collision at {key}; no overwrite")
        else:
            inserts.append(expected)
        mappings.append({"row": section["row"], "title": section["title"], "source_key": key,
                         "topic_count": len(topic_ids), "whole_subjects": sorted(whole_codes),
                         "excluded_count": excluded, "description": description, "mapped": mapped})
    plan = {"version": 1, "workbook_sha256": parsed.digest, "mapping": MAPPING,
            "database_snapshot": fingerprint({"owner": owner, "subjects": subjects, "topics": topics, "definitions": existing}),
            "inserts": inserts, "updates": 0, "unchanged": unchanged, "unmapped": unmapped,
            "superseded": superseded, "sections": mappings, "errors": errors}
    plan["fingerprint"] = fingerprint(plan)
    return plan


def require_owner(connection, user_id: UUID, *, lock: bool = False) -> None:
    clause = " FOR UPDATE" if lock else ""
    if connection.execute(text("SELECT id FROM public.profiles WHERE id=:user_id" + clause), {"user_id": user_id}).first() is None:
        raise ValueError("Explicit owner profile does not exist")


def read_assessments(connection, user_id: UUID) -> list[dict]:
    # Only definition fields and coverage, never attempts or personal study history.
    rows = [dict(r) for r in connection.execute(text(
        "SELECT id,user_id,title,description,scheduled_at,status,source_key FROM public.assessments WHERE user_id=:user_id ORDER BY id"
    ), {"user_id": user_id}).mappings()]
    for table, column, field in (("assessment_topics", "topic_id", "topic_ids"),
                                 ("assessment_subjects", "subject_id", "subject_ids")):
        covered = defaultdict(list)
        for item in connection.execute(text(
            f"SELECT assessment_id,{column} FROM public.{table} WHERE user_id=:user_id ORDER BY display_order,{column}"
        ), {"user_id": user_id}).mappings():
            covered[str(item["assessment_id"])].append(str(item[column]))
        for row in rows:
            row[field] = covered[str(row["id"])]
    return rows


def dry_run(parsed: ParsedAssessments, user_id: UUID) -> dict:
    with get_engine().begin() as connection:
        connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
        require_owner(connection, user_id)
        subjects, topics = read_state(connection)
        return make_plan(parsed, subjects, topics, read_assessments(connection, user_id), user_id)


def migrate(parsed: ParsedAssessments, user_id: UUID, approved: dict) -> dict:
    if approved.get("errors") or not approved.get("fingerprint"):
        raise ValueError("A successful reviewed dry-run plan is required")
    with get_engine().begin() as connection:
        connection.execute(text("SET LOCAL lock_timeout = '10s'"))
        # Profile row serializes imports for this owner; curriculum is stable for mapping.
        require_owner(connection, user_id, lock=True)
        connection.execute(text("LOCK TABLE public.subjects, public.topics IN SHARE MODE"))
        subjects, topics = read_state(connection)
        before = read_assessments(connection, user_id)
        plan = make_plan(parsed, subjects, topics, before, user_id)
        if plan["errors"] or plan["fingerprint"] != approved["fingerprint"]:
            raise ValueError("Source/owner/database/mapping changed; review a fresh dry run")
        for assessment in plan["inserts"]:
            connection.execute(text(
                "INSERT INTO public.assessments(id,user_id,title,description,scheduled_at,status,source_key) "
                "VALUES (:id,:user_id,:title,:description,:scheduled_at,:status,:source_key)"
            ), {field: assessment[field] for field in ("id", "user_id", *FIELDS)})
            for table, field, column in (("assessment_topics", "topic_ids", "topic_id"),
                                         ("assessment_subjects", "subject_ids", "subject_id")):
                for order, coverage_id in enumerate(assessment[field]):
                    connection.execute(text(
                        f"INSERT INTO public.{table}(assessment_id,user_id,{column},display_order) "
                        f"VALUES (:assessment_id,:user_id,:coverage_id,:display_order)"
                    ), {"assessment_id": assessment["id"], "user_id": user_id, "coverage_id": coverage_id, "display_order": order})
        after = read_assessments(connection, user_id)
        verified = make_plan(parsed, subjects, topics, after, user_id)
        if verified["errors"] or verified["inserts"] or verified["unchanged"] != len(parsed.sections):
            raise ValueError("Post-insert verification failed; rollback")
        if len(after) != len(before) + len(plan["inserts"]):
            raise ValueError("Unexpected definition count change; rollback")
        return {**plan, "inserted": len(plan["inserts"]), "verified": verified["unchanged"]}


def write_report(parsed: ParsedAssessments, plan: dict, path: Path, committed: bool = False) -> None:
    def safe(value):
        return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    lines = ["# Project 1 assessment " + ("migration" if committed else "dry run"), "",
             f"Workbook SHA-256: `{parsed.digest}`.", "",
             "Mode: " + ("transactional insert; post-write checks passed" if committed else "read-only; zero database writes"), "",
             f"Definitions: {len(parsed.sections)}; proposed inserts: {len(plan['inserts'])}; updates: 0; unchanged: {plan['unchanged']}; critical errors: {len(plan['errors'])}.",
             "Dates imported: 0; attempts/results imported: 0."]
    if committed:
        lines.append(f"Inserted: {plan['inserted']}; matching definitions verified: {plan['verified']}.")
    lines += ["", "Only literal subject-column coverage is considered. Exact subject and whitespace-normalized title matching; no aliases or fuzzy matches. Literal MONTLY titles retained. No dates, scores, attempts, completion checkboxes or private history imported. Explicit fifth-section AP All topics supersedes its individual AP topic labels.", "",
              "## Definitions and coverage", "", "| Source | Literal title | Selected topics | Whole subjects | Excluded entries |", "| --- | --- | ---: | --- | ---: |"]
    for section in plan["sections"]:
        lines.append(f"| ASSESSMENTS!A{section['row']} | {safe(section['title'])} | {section['topic_count']} | {', '.join(section['whole_subjects']) or 'none'} | {section['excluded_count']} |")
    lines += ["", "### Coverage descriptions", ""]
    lines += [f"- ASSESSMENTS!A{section['row']}: {safe(section['description'])}" for section in plan["sections"]]
    lines += ["", "## Source mappings", "", "| Source | Subject | Source label | Matched topic / scope |", "| --- | --- | --- | --- |"]
    for section in plan["sections"]:
        for mapping in section["mapped"]:
            lines.append(f"| {mapping['locator']} | {mapping['subject']} | {safe(mapping['label'])} | {safe(mapping['topic_code'] or mapping['scope'])} |")
    lines += ["", "## Excluded and unresolved source entries", ""]
    for row in plan["unmapped"] + parsed.skipped + plan["superseded"]:
        label = safe(row["label"]) if row["label"] else "nonliteral cell (value omitted)"
        lines.append(f"- {row['locator']} ({row['subject']}): {label}; {row['reason']}.")
    lines += ["", "## Blocking conflicts", ""]
    lines += ["- " + safe(error) for error in plan["errors"]] or ["None."]
    lines += ["", "Insert-only provenance: project-1:ASSESSMENTS:A<section-row>, unique per explicit owner. Existing edits, source-key conflicts or unkeyed same-title candidates block writes. Owner profile lock and in-transaction re-plan protect commit; the local approval manifest has fingerprints only. No owner identifiers, account details or private database contents are reported.", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    manifest = {field: plan[field] for field in ("version", "workbook_sha256", "fingerprint", "errors")}
    path.with_suffix(".plan.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "data/imports/Project 1.xlsx")
    parser.add_argument("--user-id", type=UUID, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--approved-plan", type=Path)
    args = parser.parse_args()
    report = args.report or ROOT / f"data/imports/reports/project-1-assessment-{'migration' if args.commit else 'dry-run'}.md"
    if args.commit and (not args.approved_plan or report.with_suffix(".plan.json").resolve() == args.approved_plan.resolve()):
        parser.error("--commit requires a successful --approved-plan and separate --report")
    committed = False
    try:
        parsed = parse_assessment_workbook(args.workbook)
        if args.commit:
            plan = migrate(parsed, args.user_id, json.loads(args.approved_plan.read_text(encoding="utf-8")))
            committed = True
        else:
            plan = dry_run(parsed, args.user_id)
        write_report(parsed, plan, report, committed)
        print(f"Definitions {len(parsed.sections)}; inserts {len(plan['inserts'])}; updates 0; unchanged {plan['unchanged']}; unresolved {len(plan['unmapped'])}; errors {len(plan['errors'])}.")
        return 1 if plan["errors"] else 0
    except Exception as error:
        print(f"Assessment import stopped ({type(error).__name__}). " + ("Database committed and verified; regenerate report with a dry run." if committed else "No partial transaction committed; inspect setup/report."))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
