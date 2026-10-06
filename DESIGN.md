# DESIGN.md

## Direction

CPA Study Hub should feel like a focused, modern study command center—not a school portal, generic admin template, or spreadsheet clone.

Qualities:

- dark-first
- information-dense but calm
- professional
- study-oriented
- easy to scan
- responsive
- minimal decoration

## Application shell

### Desktop

- left sidebar
- top utility/header area
- main content area

Sidebar:

- Dashboard
- Study Plan
- Subjects
  - FAR
  - AFAR
  - MAS
  - TAX
  - RFBT
  - AT
  - AP
- Recall
- Flashcards
- Quizzes
- Library
- Assessments
- Analytics
- Settings

### Tablet

- collapsible sidebar
- preserve hierarchy
- do not squeeze desktop cards into unusable widths

### Mobile

- drawer/compact navigation
- one primary column
- secondary content follows the main task
- comfortable touch targets
- no essential hover-only behavior

## Dashboard hierarchy

Prioritize:

1. Today's study plan
2. Overall progress
3. Recall due/overdue
4. Subject progress
5. Upcoming assessment
6. Weekly study time
7. Recent resources

Avoid giving every metric equal visual weight.

## Subject page

Header:

- subject code/name
- overall subject progress
- key status summary

Sections/tabs:

- Overview
- Topics
- Lectures
- Resources
- Quizzes
- Analytics

## Calendar

Views:

- Month
- Week
- Day

Capabilities:

- click empty date/time to add
- click event to inspect/edit
- reschedule
- mark complete
- recurring sessions
- unscheduled tasks panel where useful

Use restrained subject color markers instead of large saturated event blocks everywhere.

## Resource library

Primary controls:

- upload
- search
- filter by type/subject

Resource item shows:

- title/filename
- type
- subject/topic
- size/page count when available
- processing state
- generated quiz/flashcard counts when available

## Quiz UI

Prioritize:

- question
- answer choices
- progress
- optional timer
- submit/next action

After answering:

- explanation
- source reference
- next action

Results:

- score
- topic breakdown
- mistakes
- review mistakes
- create flashcards from mistakes

## Flashcards

One card at a time.

Front: prompt.
Back: concise answer/explanation.

Ratings:

- Forgot
- Hard
- Good
- Easy

Deck/progress context should be visible but secondary.

## Analytics

Use charts only for real comparisons/trends.

Prefer:

- line charts for time trends
- bars for subject/topic comparisons
- compact metrics for single values

No decorative charts.

## States

Major features need intentional:

- empty
- loading
- error
- success
- partially configured

## Motion

Low-to-moderate motion.

Useful for:

- navigation transitions
- modal/drawer entry
- flashcard flip
- progress updates
- drag/drop feedback

No ambient animation.

## Density

Medium-high. Show useful study information without clutter.

## Accessibility

- keyboard controls
- visible focus
- sufficient contrast
- no information by color alone
- semantic forms/labels
- responsive text
