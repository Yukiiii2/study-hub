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

## Implemented frontend design system

The application uses Geist with a deep slate canvas, sage actions and soft neutral text.
Keep this system consistent when refining or adding frontend views:

- `frontend/src/styles/tokens.css` owns semantic colors, spacing, typography, radii and control sizes.
- `frontend/src/styles/application.css` owns the shell and domain presentation.
- `frontend/src/styles/system.css` owns shared controls, composition and responsive refinements.
- `frontend/src/styles/globals.css` imports these files in that order after Tailwind.

Use the existing `ui-panel`, `ui-toolbar`, `ui-section-heading` and `ui-metrics`
patterns before introducing another surface or layout variant. Navigation icons
come from `InterfaceIcon`; labels remain visible and active routes use `aria-current`.
Dashboard and Study Plan share `PageHeader` and `SummaryMetric`; summary values
come from existing responses or counts of the currently loaded lists. Loading or
failed event requests show an unavailable value rather than a fabricated zero.

The canvas is `#0B1114`, sidebar `#10191D`, cards `#132026` and raised controls
`#1D2D34`. Primary text is `#F3F7F5`, secondary text `#B9C7C1` and quiet metadata
`#8A9A93`. Sage `#7FB69B` identifies primary actions; `#93C8AE` provides hover
contrast. Warm `#D9C27A` highlights recall/task summaries. Soft 8% white borders
and layered surfaces provide separation without decorative gradients or heavy shadows.
Primary, secondary, ghost and danger buttons retain distinct semantic treatments.

Spacing follows 4, 8, 12, 16, 20, 24, 32, 40 and 48 pixels. Controls use an
8-pixel radius, panels 12 pixels, and dialogs 16 pixels. Buttons and form controls
are at least 44 pixels high; compact heatmap dates expand to 44 pixels for touch.
Forms use 16-pixel text on narrow screens and touch devices.
Native dialogs keep their focus handling and fit within the available viewport.

The shell switches to compact navigation on tablet/mobile; Escape closes its
disclosure and returns focus. The planner switches to an agenda whenever its
content area is too narrow for the calendar, including alongside the desktop
sidebar. Resource tables retain a labeled, keyboard-focusable scroll region.
Analytics heatmap dates can be selected with keyboard, pointer or touch to show
their actual recorded values. Empty/loading/error states retain feature-specific
recovery actions and never substitute fabricated study data.
