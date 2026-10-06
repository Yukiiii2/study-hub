"""Report-only source dry run. This module has no database access or commit mode."""
import argparse
from pathlib import Path

from app.parsers.schedule_workbook import inspect_schedule

ROOT = Path(__file__).resolve().parents[3]


def report(result: dict) -> str:
    rows = ["# Project 1 schedule / calendar dry-run inspection", "",
            f"Workbook: `{result['filename']}`; SHA-256 `{result['digest']}`.", "",
            "Read-only source inspection; no database access or target account. "
            "Proposed event/task/session inserts: **0**; updates: **0**.", "",
            "## Detected source structure", "",
            f"- SCHEDULE stored range {result['schedule_extent']}: {result['weekly_blocks']} weekly blocks, "
            f"{result['schedule_dates']} literal date headers. Target-date/countdown helpers are excluded.",
            f"- Calendar stored range {result['calendar_extent']}: {result['months']} month headers, "
            f"{result['days']} validated day cells, {len(result['grid_errors'])} grid errors.",
            f"- Calendar has {result['text_cells']} text cells with supported day context and "
            f"{result['unassigned_text_cells']} without it. These are not normalized event counts.",
            f"- Non-midnight date/time values: {result['exact_times']}. Date-only Excel midnight values "
            "are not study start/end times. No exact study-block durations are supplied.", "",
            "| Weekday | Source mapping |", "| --- | --- |",
            "| Monday | RFBT |", "| Tuesday | AFAR |",
            "| Wednesday | AT/AUD; explicit AT and AP row references distinguish subjects |",
            "| Thursday | MS normalized to MAS |", "| Friday | TAX |", "| Saturday | FAR |",
            "| Sunday | Recall/backlogs/rest; no invented subject or activity type |", "",
            "## Topic-reference inspection", "",
            f"- {result['mapped_refs']} of {result['direct_refs']} direct references resolve to accepted "
            "curriculum source rows. Formula syntax is traced, never executed.",
            "- Unresolved direct references: " + (", ".join("SCHEDULE!" + c for c in result["invalid_refs"]) or "none") + ".",
            "- Indirect references require separate tracing: " + (", ".join("SCHEDULE!" + c for c in result["indirect_refs"]) or "none") + ".",
            f"- {len(result['crossed_refs'])} references cross the weekday column subject:", ""]
    rows += [f"  - SCHEDULE!{cell}: {column} column references {subject}/{code}."
             for cell, column, subject, code in result["crossed_refs"]]
    rows += ["", "## Phase 6 import decision", "",
             "Keep both sheets report-only. Calendar labels include study, assessment, break/holiday "
             "and personal reminder material, without exact study times or a chosen authenticated owner. "
             "Do not manufacture timed events, activity types, personal progress, or ownership. "
             "Reliable day patterns remain here for the user to configure through the editable planner. "
             "Future unscheduled-task conversion requires source/ownership and ambiguous-reference review.", "",
             "## Privacy and unresolved source decisions", "",
             "Personal titles, literal calendar dates/reminders, remarks, checkbox state and credentials "
             "are omitted. The workbook stays local and ignored. No assessment table/link or later-phase "
             "production data is created. Source ambiguities do not block an initially empty editable calendar.", ""]
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=ROOT / "data/imports/Project 1.xlsx")
    parser.add_argument("--report", type=Path, default=ROOT / "data/imports/reports/project-1-schedule-dry-run.md")
    args = parser.parse_args()
    result = inspect_schedule(args.workbook)
    if result["grid_errors"]:
        raise SystemExit("Calendar grid validation failed; no import is permitted.")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report(result), encoding="utf-8")
    print(f"Schedule dry run: {result['weekly_blocks']} weeks, {result['schedule_dates']} dates; "
          f"Calendar: {result['days']} validated days. Report-only: 0 writes.")


if __name__ == "__main__":
    main()
