# Mobile presentation architecture

The working frontend remains the functional reference. This pass changes presentation only; API contracts, authentication, database access, scheduling, grading and ownership rules are unchanged.

## One controller, one mounted presentation

`components/responsive-view.tsx` selects mobile/portrait presentation below 960px and desktop/workspace presentation from 960px. It uses `useSyncExternalStore` with a shared media-query listener. Server rendering and the first hydration snapshot both return an unknown viewport and a localized skeleton. A phone never first displays a desktop layout. Only the selected presenter mounts.

Requests, mutations, timers and durable page state stay above that selection. Resizing does not refetch data. Small shell navigation and shared primitive controls may still use CSS media queries; complex calendar, dashboard and report structures do not rely on hidden duplicate DOM trees.

| Area | Controller | Dedicated presentations |
| --- | --- | --- |
| Today | `dashboard/dashboard.tsx` | `dashboard-view.tsx`, `dashboard-mobile-view.tsx` |
| Plan | `study-plan/study-planner.tsx` | `plan-desktop-view.tsx`, `plan-mobile-view.tsx` |
| Analytics | `analytics/use-analytics-data.ts` | `analytics-desktop-view.tsx`, `analytics-mobile-view.tsx` |
| Subjects | `subjects/subjects-list.tsx` | `subjects-desktop-view.tsx`, `subjects-mobile-view.tsx` |
| Subject workspace | `subjects/subject-detail.tsx` | `subject-desktop-workspace.tsx`, `subject-mobile-workspace.tsx` |
| Library list | `resources/resource-library.tsx` | `resource-desktop-list.tsx`, `resource-mobile-list.tsx` |
| Assessments | `assessments/assessment-list.tsx` | `assessment-desktop-view.tsx`, `assessment-mobile-view.tsx` |

Focus, quiz-taking and Recall retain their existing task-specific components. They use readable shared controls and a single active study surface. Flashcard management mounts only its selected Cards, Decks or History tab. Filter disclosures keep one form tree mounted, so opening them does not restart their option loaders.

## Mobile Plan

The calendar/agenda comes before the overview and actual-session management panel on mobile. Desktop keeps the established order.

- Month: Sunday-first seven-column grid with five or six rows, dates and subject indicators. No event titles or per-date Add buttons.
- Week: seven-day horizontal selector and the selected day's chronological timeline, including start/end times.
- Selecting a date updates the agenda. Add defaults to that date. Today restores today's date; previous/next navigate the displayed period.
- The existing controller supplies events to either presentation. Its fetch window includes the compact calendar's leading Sunday. Recurrence and mutation behavior are unchanged.
- Editors are outside the responsive layout selection, retaining form state when the viewport changes.

## Shell, browser chrome and forms

Standard pages use document/browser scrolling on every device. The shell and main content grow naturally, with no shell-level vertical scroller or document scroll lock. Desktop uses a sticky viewport-height sidebar (only its navigation group can scroll when needed) and a sticky utility header. Mobile navigation is fixed; main-content bottom padding reserves its full height, `env(safe-area-inset-bottom)` and content clearance. The Assistant launcher and desktop window are viewport-fixed overlays, with extra end-of-page clearance for the launcher. Dialogs, sheets, Assistant conversations, tables and bounded calendar interfaces retain local scrolling.

Viewport metadata enables `viewport-fit=cover` and Android Chrome's `interactive-widget=resizes-content`. Dialogs scroll internally, have visible close controls and sticky action rows, and retain native keyboard/Escape behavior. Physical keyboard/browser-toolbar behavior still requires device review.

`styles/mobile.css` owns mobile presenter styles and small shared mobile refinements. Spacing uses mobile gutter, panel-padding and section-gap tokens. Filters stack with 44px controls. Secondary forms can be disclosed without compressing their labels.

## Session recovery

A read-only database check found a genuinely unfinished session open for approximately 126 hours. No session was changed or deleted. Elapsed time continues to use the existing server clock plus a monotonic browser clock.

A session started on an earlier profile-local study day displays an open-session recovery message. Focus asks for explicit confirmation before saving its full elapsed duration. This is a presentation cue, not a duration cap or a new study-time rule.

## Loading and motion

- Initial data: content-shaped skeleton, with its loading label announced to assistive technology rather than repeated visually.
- Background refresh/error: retain usable data, show local status/retry and replace it only after success.
- Empty results: compact copy, no repeated primary CTA or zero-result pagination. An out-of-range page retains Previous for recovery.
- Motion: existing 160/200/280ms tokens; reduced motion removes decorative transitions.

## Review scope

Validation uses the production build in Chromium, phone/touch emulation, six phone sizes and four desktop sizes. Top/middle/bottom screenshots and populated response fixtures are kept outside Git in the ignored local QA directory. Fixtures do not persist study records; temporary Auth accounts are removed afterward. Android hardware, browser toolbar transitions, and the actual software keyboard remain client visual-approval checks.

The current visual/mobile work is approved for publication. The frontend commit is published through GitHub; the connected Vercel project handles automatic deployment.

## Changed file map

- Shared UI: `components/responsive-view.tsx`, `filter-panel.tsx`, `account-menu.tsx`, `app-shell.tsx`, `interface-icon.tsx`, `study-ui.tsx`; viewport metadata in `app/layout.tsx`.
- Presentation styles: `styles/mobile.css`, `tokens.css`, `globals.css`. The prior calendar/motion styles and icon work remain intact.
- Today: `dashboard.tsx`, `dashboard-view.tsx`, `dashboard-mobile-view.tsx`.
- Plan: `study-planner.tsx`, `plan-view-types.ts`, `plan-desktop-view.tsx`, `plan-mobile-view.tsx`, `compact-calendar.tsx`.
- Analytics: `analytics-page.tsx`, `use-analytics-data.ts`, `analytics-controls.tsx`, `analytics-desktop-view.tsx`, `analytics-mobile-view.tsx`, `analytics-charts.tsx`, `mobile-activity-calendar.tsx`, `presentation.ts`.
- Subjects: `subjects-list.tsx`, `subjects-desktop-view.tsx`, `subjects-mobile-view.tsx`, `subject-detail.tsx`, `subject-desktop-workspace.tsx`, `subject-mobile-workspace.tsx`, `topic-hierarchy.tsx`.
- Library: `resource-library.tsx`, `resource-views.tsx`, `resource-format.ts`, `resource-desktop-list.tsx`, `resource-mobile-list.tsx`.
- Assessments: `assessment-list.tsx`, `assessment-desktop-view.tsx`, `assessment-mobile-view.tsx`.
- Other targeted UI refinements: `focus/focus-page.tsx`, `flashcards/flashcard-library.tsx`, `flashcards/recall.tsx`, `quizzes/shared.tsx`, `quizzes/question-bank.tsx`, `quizzes/quiz-list.tsx`, `assistant/assistant-page.tsx`.
- Tests: new `responsive-view.cjs` and `mobile-presentations.cjs`; calendar, auth rendering, dashboard, assessment, flashcard, resource, loading, planner and study-time render fixtures/assertions updated for the selected presentation.

Feature paths above are relative to `frontend/src/features/`, shared paths to `frontend/src/`, and test paths to `frontend/tests/`. Earlier uncommitted calendar date/icon/motion changes were preserved. No backend files changed.

## Validation record

- Production build, TypeScript and all 18 frontend test files passed.
- Six phone viewports: 360x800, 375x812, 390x844, 400x864, 412x915, 430x932.
- Four desktop/workspace viewports: 1024x768, 1280x800, 1440x900, 1920x1080.
- Initial browser sweep: 16 primary screens across all ten sizes (160 layout checks). Resizing did not create additional API requests.
- Populated browser-response fixtures: 16 screens, including quiz taking/review, assessment detail and PDF/CSV detail, across the six phone sizes (96 layout checks).
- Targeted confirmation after the final Plan/Focus/curriculum refinements: three affected screens across those ten sizes plus 768x1024 and 820x1180 (36 layout checks).
- Checked selected-date event creation, month/Today navigation, mobile Week start/end times, editor draft preservation across mobile/desktop changes, native sheet Escape/focus behavior, 500px-high keyboard-style viewport, safe-area reservation, and synthesized touch selection.
- Checked initial skeletons, retained charts/cards/calendar during delayed requests, explicit failed-refresh/retry recovery, contained answer saves, AI generation with preserved context/input, and no automatic study-data persistence.
- No unexplained 404s, hydration/React warnings or uncaught exceptions were observed. A deliberate intercepted 503 tested recovery; it was not an unexpected service failure.
- Temporary Auth verification accounts were removed. No browser-fixture study records were written. The pre-existing unfinished session was left untouched.

These checks used Chromium emulation and local production output, not a physical Android device or a production deployment. The current presentation has received client visual approval; the physical-device checks noted above remain distinct from automated emulation.
