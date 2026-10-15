# Study Hub visual direction

## Review desk ledger

Study Hub should feel like a disciplined CPALE review desk translated into software. The interface uses neutral cool-slate planes, ruled schedules, curriculum rows, and precise progress marks. Teal identifies important actions; seven restrained subject accents identify curriculum context.

The visual hierarchy is built around one question: **what should I study now?** The strongest surface on Today is the current study docket. Everything below it explains the day, signals attention, or offers a clear continuation.

The prototype uses illustrative values to demonstrate density and hierarchy. It does not represent production data and it is not connected to the application.

## Foundations

### Color

| Token | Value | Use |
| --- | --- | --- |
| Canvas | `#090d12` | App background |
| Navigation | `#0d131a` | Sidebar and mobile navigation |
| Surface | `#111821` | Primary grouped areas |
| Elevated | `#16202a` | Controls and emphasized rows |
| Strong surface | `#1b2732` | Selected and hover states |
| Border | `#263440` at 78% opacity | Dividers and quiet outlines |
| Primary text | `#f1f4f2` | Headings and key values |
| Secondary text | `#a3afb7` | Body text |
| Muted text | `#8b99a3` | Readable metadata; lifted from the directional value |
| Teal | `#65bfae` | Important actions, Focus, links, selected controls |
| Teal hover | `#78ccba` | Hover and keyboard focus support |
| Teal subtle | `#193931` | Focus controls only |
| Success | `#74b992` | Completed state |
| Warning | `#d6ad5d` | Due recall and deadlines |
| Information | `#76afc6` | Lecture and informational state |
| Danger | `#d4777f` | Errors and overdue state |

### Subject identity

Subject color is used as a dot, 2px rule, tag mark, chart mark, or progress fill. Text labels always accompany it.

| Subject | Accent |
| --- | --- |
| FAR | `#7eb7d8` — cool blue |
| AFAR | `#a99ad9` — lavender |
| MAS | `#79c3a6` — mint |
| TAX | `#e2c16d` — warm amber |
| RFBT | `#d98c9d` — muted rose |
| AT | `#76afc6` — cool cyan |
| AP | `#e79b72` — soft coral |

Semantic states remain separate from subject identity. A TAX marker indicates subject context; an amber due badge indicates urgency. Labels always explain the distinction.

### Typography

- Family: Geist or the application's current neutral sans serif.
- Page title: 30/36 desktop, 26/32 tablet, 24/30 mobile; weight 620.
- Section title: 18/24; weight 600.
- Card or row title: 14–15/20; weight 580.
- Body: 14/21 desktop and 14/20 mobile.
- Metadata: 12/17; use uppercase only for short structural labels.
- Timer and tabular data: tabular numerals in the same family. Monospace is not a decorative motif.

### Spacing and geometry

- Spacing scale: 4, 8, 12, 16, 24, 32, 40, 48.
- Page gutters: 28 desktop (22 at compact laptop widths), 24 tablet, 14 mobile.
- Main content max width: 1240px.
- Radii: 8px controls, 12px panels, 14px dialogs. Pills are reserved for filters and compact statuses.
- Borders: 1px neutral dividers. Subject edge marks may use 2px.
- Shadows: only on dialogs and mobile sheets; no routine card shadows.

## Component rules

- **Page header:** title and one-line orientation on the left; at most two actions on the right.
- **Primary button:** filled teal, dark text, minimum 44px target.
- **Secondary button:** elevated charcoal with a neutral border.
- **Ghost button:** no persistent container; surface appears on hover/focus.
- **Danger button:** muted red outline or fill, used only for destructive actions.
- **Tabs:** a compact ruled row with a 2px selected underline. Segmented controls use one shared surface.
- **Badges:** concise status words with an icon or text cue; status is never color-only.
- **Inputs:** 44px minimum height, visible labels, muted helper text, teal focus outline.
- **Lists:** prefer aligned rows and dividers over a card per item.
- **Empty state:** short title, useful next step, and one relevant action; no large illustration.
- **Loading state:** preserve page structure with quiet skeleton rows.
- **Error state:** place the message near the failed content with Retry; reserve red for the error cue.
- **Charts:** direct labels, restrained grid lines, subject accents, and accessible text summaries.
- **Dialog/mobile sheet:** one clear title, persistent close affordance, contained scrolling, and actions kept visible.

## Navigation

Desktop uses a 216px grouped sidebar. Today, Plan, and Study establish the main study loop. Practice and Progress remain available without competing with the current action. Focus is a persistent sage-accented control. Account and settings stay at the bottom.

Tablet portrait removes the sidebar. A compact top bar provides identity and utility actions; a five-item bottom navigation keeps Today, Plan, Focus, Study, and More within reach.

Mobile uses the same five destinations. Focus occupies the central position with a stronger icon treatment inside the navigation bounds. Secondary product areas live under More.

### Content-safe mobile/tablet shell

The shell is a fixed-height flex column. Header, optional tablet date row, scrollable main, and opaque bottom navigation are siblings. Only main scrolls (`flex: 1; min-height: 0; overflow-y: auto`). Navigation uses `position: sticky; bottom: 0` while retaining its normal-flow row: a 68px base height plus `env(safe-area-inset-bottom)`. Its five targets are at least 58px high. No negative offsets extend navigation into content. It stays visible at the viewport bottom during scrolling.

The main has 28px end padding for breathing room, rather than page-specific padding to compensate for an overlay. The final section can always scroll fully above navigation. A shared `--shell-safe-area` token allows the render check to simulate a 34px device inset.

At 960px and wider in landscape, the tablet prototype replaces bottom navigation with a 76px workspace rail. Labeled 54px navigation targets, a distinct Focus action, and the account control occupy a separate grid column. The main remains independently scrollable beside the rail. Portrait tablet keeps bottom navigation.

## Representative compositions

### Dashboard

The study docket is the first and strongest region. It combines the current/next event, context, time, and one Start Focus action. Today is a ruled agenda instead of a set of cards. Attention items sit beside the agenda on desktop and immediately after it on smaller screens. Continue studying, concise progress, seven-day activity, and subject status follow in decreasing priority.

### Focus

The active timer removes utility noise and reduces navigation contrast. Subject, topic, activity, and start time remain visible around a large tabular timer. Finish is the only high-emphasis action. Setup uses the same composition with selectors and a Start action. There is no pause control because the current product does not support pause.

Mobile groups context, timer, start information, objective, Finish, and today's time into one compact surface. The group is safely centered in the available main area instead of stretching the timer panel. The daily total is directly attached below Finish rather than separated by empty space. If space becomes insufficient, safe alignment and scrolling preserve access to the first and last controls.

### Analytics

The representative page reads as one report: period and summary, daily activity, time allocation, planned versus actual, and session history. Metrics share a summary rail instead of separate cards. The main activity plot has one quiet surface; breakdowns and comparisons use spacing and dividers. Actual-time comparison bars use their subject accent, while planned bars remain neutral.

### Subject workspace

The subject identity anchors the header and persists through topic markers, lecture progress, and actions. A compact progress rail supports Start Focus and Continue Lecture. Topics and lectures form one workspace with curriculum rows, status, and contextual tools rather than a simple binary switch.

FAR receives a 2px blue header marker and a clearer outlined subject badge. Existing blue progress and selected curriculum marks provide continuity without tinting the workspace.

### Design System reference

The **Design System** gallery tab is an approval artifact only. It shows button variants (including disabled and loading), labeled inputs, search, select, textarea, checkbox/radio, keyboard-operable tabs, segmented controls, subject markers, progress, table rows, feedback notices, skeleton/empty/error/retry states, and static dialog/sheet anatomy. Hover and focus examples appear alongside actual keyboard focus styles.

Dialog and sheet examples are deliberately static, not active modal implementations. The reference records the required focus trap, Escape behavior, focus restoration, close action, contained scrolling, and device insets for later implementation. None of these samples creates or saves study data.

## Responsive behavior

- Desktop keeps persistent navigation and uses adjacent information only when the relationship improves comparison.
- Tablet composes content into one primary column plus occasional paired summaries; touch targets grow while density remains useful.
- Mobile is task-first. The next action, today, and due work appear before progress. Dense tables become labeled rows. The bottom navigation remains visible and dialogs become sheets.
- At every size, source order matches reading order and no horizontal page scrolling is required.
- At approximately 1024px landscape, the tablet dashboard uses the compact rail and adjacent agenda/attention regions. Desktop prototypes compact their sidebar and stack only the sections that need more space.

## Prototype

Open [`prototype/index.html`](prototype/index.html) in a browser. It contains an editable HTML/CSS review surface for the seven representative screens plus Design System and links to each view at its intended viewport. The generated PNGs in [`renders/`](renders/) are fixed review snapshots.

The review toolbar includes viewport presets and Page top / Page end positions. Mobile is available at 390×844 and 430×932; tablet at 768×1024, 820×1180, and 1024×768; desktop views at 1440×900, 1366×768, and 1024×768.

Reproduce the render matrix with `node docs/visual-direction/prototype/render.cjs` on this Windows machine with Edge installed. The renderer checks horizontal overflow, navigation separation, touch-target height, final-content reachability, and a simulated safe-area inset. Results are in [`renders/validation.json`](renders/validation.json). Top and end screenshots make the scrolling behavior reviewable.

See [`VALIDATION.md`](VALIDATION.md) for the refinement checks and measured text contrast.

This directory is isolated from `frontend/`; it does not import application code or alter production behavior.
