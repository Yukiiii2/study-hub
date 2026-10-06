# Project 1 schedule / calendar dry-run inspection

Workbook: `Project 1.xlsx`; SHA-256 `47679efde3b0bd0317cc7c9bd11589bc3a781289e5e13fb916117820ee7de01e`.

Read-only source inspection; no database access or target account. Proposed event/task/session inserts: **0**; updates: **0**.

## Detected source structure

- SCHEDULE stored range A1:V89: 19 weekly blocks, 133 literal date headers. Target-date/countdown helpers are excluded.
- Calendar stored range A1:Z1015: 9 month headers, 273 validated day cells, 0 grid errors.
- Calendar has 86 text cells with supported day context and 0 without it. These are not normalized event counts.
- Non-midnight date/time values: 0. Date-only Excel midnight values are not study start/end times. No exact study-block durations are supplied.

| Weekday | Source mapping |
| --- | --- |
| Monday | RFBT |
| Tuesday | AFAR |
| Wednesday | AT/AUD; explicit AT and AP row references distinguish subjects |
| Thursday | MS normalized to MAS |
| Friday | TAX |
| Saturday | FAR |
| Sunday | Recall/backlogs/rest; no invented subject or activity type |

## Topic-reference inspection

- 152 of 153 direct references resolve to accepted curriculum source rows. Formula syntax is traced, never executed.
- Unresolved direct references: SCHEDULE!L77.
- Indirect references require separate tracing: SCHEDULE!C22, SCHEDULE!C35, SCHEDULE!F76.
- 13 references cross the weekday column subject:

  - SCHEDULE!F70: AFAR column references RFBT/RFBT-19A.
  - SCHEDULE!L70: MAS column references AP/AP-18.
  - SCHEDULE!F73: AFAR column references RFBT/RFBT-20A.
  - SCHEDULE!C76: RFBT column references TAX/TAX-17.
  - SCHEDULE!L76: MAS column references TAX/TAX-18.
  - SCHEDULE!C79: RFBT column references FAR/FAR-35.
  - SCHEDULE!F79: AFAR column references FAR/FAR-38.
  - SCHEDULE!L79: MAS column references FAR/FAR-43.
  - SCHEDULE!O79: TAX column references FAR/FAR-44.
  - SCHEDULE!C80: RFBT column references FAR/FAR-37.
  - SCHEDULE!F80: AFAR column references FAR/FAR-39.
  - SCHEDULE!O80: TAX column references FAR/FAR-45.
  - SCHEDULE!F81: AFAR column references FAR/FAR-40.

## Phase 6 import decision

Keep both sheets report-only. Calendar labels include study, assessment, break/holiday and personal reminder material, without exact study times or a chosen authenticated owner. Do not manufacture timed events, activity types, personal progress, or ownership. Reliable day patterns remain here for the user to configure through the editable planner. Future unscheduled-task conversion requires source/ownership and ambiguous-reference review.

## Privacy and unresolved source decisions

Personal titles, literal calendar dates/reminders, remarks, checkbox state and credentials are omitted. The workbook stays local and ignored. No assessment table/link or later-phase production data is created. Source ambiguities do not block an initially empty editable calendar.
