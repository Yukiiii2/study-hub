"""Dry-run-first video extension of the Project 1 curriculum migration."""
import argparse
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy import text

from app.db.connection import get_engine
from app.parsers.video_workbook import MAPPING, ParsedVideos, parse_video_workbook
from app.parsers.curriculum_workbook import SUBJECT_SHEETS
from app.services.curriculum_import import ROOT, fingerprint, read_state, make_plan as curriculum_plan

FIELDS = ("topic_id", "title", "duration_seconds", "source_url", "source_code", "display_order")


def read_videos(connection) -> list[dict]:
    return [dict(r) for r in connection.execute(text(
        "SELECT id, topic_id, title, duration_seconds, source_url, source_code, display_order FROM public.videos ORDER BY id"
    )).mappings()]


def make_plan(parsed: ParsedVideos, subjects: list[dict], topics: list[dict], existing: list[dict]) -> dict:
    baseline = curriculum_plan(parsed.curriculum, subjects, topics)
    errors = list(parsed.errors) + baseline["errors"]
    if baseline["inserts"]:
        errors.append("Real Phase 4 topics are missing; video import does not create curriculum")
    subject_map = {str(r["id"]): r["code"] for r in subjects}
    topic_map = {(subject_map.get(str(r["subject_id"])), r["code"]): r for r in topics}
    topic_ids = {str(r["id"]) for r in topics}
    locators, titles, ids = {}, set(), set()
    for row in existing:
        topic_id = str(row["topic_id"])
        if topic_id not in topic_ids:
            errors.append(f"Orphan existing video {row['id']}")
        key = (topic_id, row["title"].casefold())
        if key in titles:
            errors.append(f"Duplicate existing video title for topic {topic_id}")
        titles.add(key)
        if str(row["id"]) in ids:
            errors.append("Duplicate existing video identity")
        ids.add(str(row["id"]))
        if row["source_code"]:
            if row["source_code"] in locators:
                errors.append(f"Duplicate existing source locator {row['source_code']}")
            locators[row["source_code"]] = row
    inserts, unchanged, unmapped, aliases = [], 0, [], []
    source_titles = set()
    for row in parsed.videos:
        code = MAPPING["topic_aliases"].get(f"{row['subject']}/{row['code']}", row["code"])
        topic = topic_map.get((row["subject"], code))
        if topic is None:
            unmapped.append({"sheet": row["sheet"], "row": row["row"], "code": row["code"]})
            errors.append(f"Unmapped topic {row['sheet']}!{row['row']} ({row['code']}); no guessing")
            continue
        if code != row["code"]:
            aliases.append({"sheet": row["sheet"], "row": row["row"], "source": row["code"], "topic": code})
        topic_id = str(topic["id"])
        title_key = (topic_id, row["title"].casefold())
        if title_key in source_titles:
            errors.append(f"Duplicate source title after topic mapping {row['source_code']}; no automatic merge")
            continue
        source_titles.add(title_key)
        expected = {"id": str(uuid5(NAMESPACE_URL, f"study-hub/project-1/videos/v1/{topic_id}/{row['source_code']}")),
                    "topic_id": topic_id, **{field: row[field] for field in FIELDS if field != "topic_id"}}
        actual = locators.get(row["source_code"])
        if actual:
            if any(str(actual[f]) != str(expected[f]) for f in FIELDS):
                errors.append(f"Existing video conflict {row['source_code']}; no overwrite")
            else:
                unchanged += 1
        elif expected["id"] in ids or (topic_id, row["title"].casefold()) in titles:
            errors.append(f"Existing identity/title collision {row['source_code']}; source relocation requires review")
        else:
            inserts.append(expected)
    plan = {"version": 1, "workbook_sha256": parsed.curriculum.digest, "mapping": MAPPING,
            "database_snapshot": fingerprint({"subjects": subjects, "topics": topics, "videos": existing}),
            "inserts": inserts, "updates": 0, "unchanged": unchanged, "unmapped": unmapped,
            "aliases": aliases, "errors": errors}
    plan["fingerprint"] = fingerprint(plan)
    return plan


def migrate(parsed: ParsedVideos, approved: dict) -> dict:
    if approved.get("errors") or not approved.get("fingerprint"):
        raise ValueError("A validated dry-run plan is required")
    with get_engine().begin() as connection:
        connection.execute(text("SET LOCAL lock_timeout = '10s'"))
        connection.execute(text("LOCK TABLE public.subjects, public.topics IN SHARE MODE"))
        connection.execute(text("LOCK TABLE public.videos IN SHARE ROW EXCLUSIVE MODE"))
        subjects, topics = read_state(connection)
        before = read_videos(connection)
        plan = make_plan(parsed, subjects, topics, before)
        if plan["errors"] or plan["fingerprint"] != approved["fingerprint"]:
            raise ValueError("Source/database/mapping changed; review a fresh dry run")
        if plan["inserts"]:
            connection.execute(text(
                "INSERT INTO public.videos(id, topic_id, title, duration_seconds, source_url, source_code, display_order) "
                "VALUES (:id, :topic_id, :title, :duration_seconds, :source_url, :source_code, :display_order)"
            ), plan["inserts"])
        after = read_videos(connection)
        verified = make_plan(parsed, subjects, topics, after)
        if verified["errors"] or verified["inserts"] or verified["unchanged"] != len(parsed.videos):
            raise ValueError("Post-import validation failed; rollback")
        if len(after) != len(before) + len(plan["inserts"]):
            raise ValueError("Unexpected count change; rollback")
        return {**plan, "inserted": len(plan["inserts"]), "verified": verified["unchanged"]}


def write_report(parsed: ParsedVideos, plan: dict, path: Path, committed: bool) -> None:
    def safe(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["# Project 1 video " + ("migration" if committed else "dry run"), "",
             f"Workbook: `{parsed.curriculum.filename}`; SHA-256 `{parsed.curriculum.digest}`.", "",
             "Mode: " + ("transactional insert; post-write checks passed" if committed else "read-only; zero database writes"), "",
             f"Proposed inserts: {len(plan['inserts'])}; updates: 0; unchanged: {plan['unchanged']}; critical errors: {len(plan['errors'])}."]
    if committed:
        lines.append(f"Inserted: {plan['inserted']}; verified matching videos: {plan['verified']}.")
    lines += ["", "## Sheets, mapping, and counts", "", "| Sheet | Subject | Candidates | Accepted | Excluded conflicts | Invalid durations |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for base, subject in SUBJECT_SHEETS.items():
        lines.append(f"| {base} Vids | {subject} | {parsed.candidates[subject]} | {sum(r['subject']==subject for r in parsed.videos)} | {sum(r['subject']==subject for r in parsed.excluded)} | {sum(r['subject']==subject for r in parsed.invalid_durations)} |")
    lines += ["", f"Accepted: {len(parsed.videos)}; mapped: {len(parsed.videos)-len(plan['unmapped'])}; unmapped/ambiguous topic mappings: {len(plan['unmapped'])}; invalid titles: {sum(e.startswith('Invalid title') for e in parsed.errors)}; unexpected duplicate source titles: {len(parsed.duplicates)}.", "",
              "## Extraction, identity, and durations", "",
              "A literal topic code, B literal lecture title, C duration; uncoded section/total rows and formatting blanks are not videos. MS maps to MAS. Exact existing topic codes are required, with the reviewed RFBT-11A -> RFBT-11a alias at rows 98–99. No topic or title is invented. All real Phase 4 topics are checked before video planning.", "",
              "source_code is an import locator (project-1:worksheet:row), not a new curriculum/lecture code. Topic UUID plus that locator determines UUIDv5. Existing exact matches retain their IDs. Changed fields, relocated identities/titles, duplicate locators/titles, or missing topics block writes; no updates, deletes, or merges. Source/mapping/database fingerprints are rechecked under locks inside the insert transaction. display_order is the original worksheet row.", "",
              "Confirmed display semantics: h:mm values encode MM:SS; [h]:mm:ss values with zero final stored seconds encode elapsed MM:SS (e.g. stored 57:27:00 -> lecture 57:27). h:mm:ss encodes real HH:MM:SS. Raw XML serials preserve elapsed hours before reader conversion; they reconstruct the confirmed display semantics, never literal time-of-day durations. Numeric rounding tolerance is 0.01 stored seconds. Unrecognized/negative/formula/error durations are never guessed. Explicit confirmed source corrections: FAR C294 23.59 -> 23:59, FAR C295 24.46 -> 24:46, TAX C64 27:08: -> 27:08; corrections require exact original values.", "",
              "## Unresolved source-data conflicts", "",
              "FAR Vids rows 586–587 both say **42-04 Exercise 2**, referencing FAR-42, but durations differ (48:23 and 48:22). Both excluded by client approval. They require client/source clarification. Neither renamed, merged, nor assigned an invented distinguishing title.", "",
              "## Errors, unmapped rows, invalid durations", ""]
    lines += ["- " + safe(e) for e in plan["errors"]]
    lines += ["- " + safe(r) for r in parsed.invalid_durations + plan["unmapped"]]
    if not plan["errors"] and not parsed.invalid_durations and not plan["unmapped"]:
        lines.append("None; approved two-row exclusion remains unresolved and is not an import candidate.")
    lines += ["", "## Skipped labels", ""]
    lines += [f"- {r['sheet']}!{r['row']}: {safe(r['title'])}; {r['reason']}." for r in parsed.skipped]
    lines += ["", "## Accepted source traceability", ""]
    if not committed and plan["unchanged"] == 0:
        lines += ["| Subject | Source | Topic reference | Title | Seconds |", "| --- | --- | --- | --- | ---: |"]
        lines += [f"| {r['subject']} | {r['sheet']}!{r['row']} | {r['code']} | {safe(r['title'])} | {r['duration_seconds']} |" for r in parsed.videos]
    else:
        lines.append("Full source/title/duration traceability is in the [initial video dry run](project-1-video-dry-run.md) and the adjacent local .source-plan.json. Source SHA-256 above identifies the workbook verified for this report.")
    lines += ["", "Workbook completion checkboxes, personal remarks/history, and credentials are excluded. Zero user progress rows are imported. Recall, schedules/calendar, assessments, and all later domains remain deferred. The source workbook and JSON manifests remain ignored and local.", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    path.with_suffix(".plan.json").write_text(json.dumps(plan, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    path.with_suffix(".source-plan.json").write_text(json.dumps(parsed.videos, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "data/imports/Project 1.xlsx")
    parser.add_argument("--report", type=Path, default=ROOT / "data/imports/reports/project-1-video-dry-run.md")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--approved-plan", type=Path)
    args = parser.parse_args()
    if args.commit and (not args.approved_plan or args.report.with_suffix(".plan.json").resolve() == args.approved_plan.resolve()):
        parser.error("--commit requires a successful --approved-plan and separate --report")
    committed = False
    try:
        parsed = parse_video_workbook(args.workbook)
        if args.commit:
            plan = migrate(parsed, json.loads(args.approved_plan.read_text(encoding="utf-8")))
            committed = True
        else:
            with get_engine().begin() as connection:
                connection.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"))
                subjects, topics = read_state(connection)
                plan = make_plan(parsed, subjects, topics, read_videos(connection))
        write_report(parsed, plan, args.report, args.commit)
        print(f"Accepted {len(parsed.videos)}; inserts {len(plan['inserts'])}; updates 0; unchanged {plan['unchanged']}; errors {len(plan['errors'])}.")
        return 1 if plan["errors"] else 0
    except Exception as error:
        print(f"Video import stopped ({type(error).__name__}). " + ("Database committed and verified; regenerate report with a dry run." if committed else "No partial transaction committed; inspect setup/report."))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
