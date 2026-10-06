# DESIGN_GUIDELINES.md

## Visual language

- Dark-first interface.
- Neutral near-black/charcoal surfaces.
- Slightly lighter grouped surfaces.
- Prefer thin borders over shadows.
- One primary application accent.
- Subject colors identify subjects but do not dominate pages.
- Avoid visual noise.

## Typography

- prioritize readability
- clear sans-serif UI typeface
- strong hierarchy: page title, section title, metric, body, metadata
- avoid excessive all-caps
- avoid tiny metadata text

## Spacing

- use a consistent scale
- keep readable page gutters
- denser data views may use tighter internal spacing
- do not wrap every section in another card

## Cards/surfaces

Use cards only for meaningful grouping.

Avoid:

- excessive nested cards
- every metric as a giant tile
- oversized border radius
- heavy shadows
- glassmorphism by default
- decorative gradients

## Buttons

Primary:
- accent color
- reserved for main actions

Secondary:
- neutral/bordered

Destructive:
- visually distinct
- confirmation when appropriate

Do not turn every action into a pill.

## Navigation

- active route obvious
- subject navigation easy to scan
- collapsed navigation remains accessible
- avoid duplicate competing primary navigation

## Forms

- visible labels
- specific validation
- clear date/time inputs
- import preview before bulk insertion
- no placeholder-only labels

## Subject identity

Subject colors may be used for:

- small markers
- progress accents
- event identifiers
- chart series

Do not use bright full-page subject backgrounds.

## Tables/lists

For topics/videos/questions/imports:

- clear column hierarchy
- responsive alternative on narrow screens
- sticky headers only when useful
- concise statuses
- avoid needless horizontal overflow

## Calendar

- distinguish type and subject without overwhelming color
- completed items remain readable
- overdue/due state is not color-only
- drag/drop must have a non-drag edit alternative

## Quiz

- one clear question focus
- comfortable answer targets
- unmistakable answer state
- explanation after submission
- source references secondary but discoverable

## Flashcards

- concise readable content
- keyboard + pointer interaction
- distinct review ratings
- restrained flip animation

## Responsive

At small widths:

- single-column primary flow
- tables may become stacked rows/cards
- sidebar becomes drawer/compact navigation
- dialogs fit without clipped controls
- no essential hover-only behavior

## Consistency

Before creating a new component pattern, check whether an existing project pattern already solves the problem.

Do not redesign unrelated surfaces during feature work.
