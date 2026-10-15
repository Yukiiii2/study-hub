// Render real dashboard states without a browser or new test dependencies.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ts = require("typescript");
const src = path.join(__dirname, "../src");
const modules = new Map();
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  const requireLocal = (name) => {
    if (name === "next/link") return { default: ({ children, ...props }) => React.createElement("a", props, children) };
    if (name === "@/services/api" || name === "./api") return { ApiError: class extends Error {} };
    if (name.startsWith("@/") || name.startsWith(".")) {
      const base = name.startsWith("@/") ? path.join(src, name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(fs.existsSync(base + ".tsx") ? base + ".tsx" : base + ".ts");
    }
    return require(name);
  };
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  vm.runInNewContext(code, { module: output, exports: output.exports, require: requireLocal, Error, Intl, Date, URLSearchParams });
  return output.exports;
}
const { Dashboard } = load(path.join(src, "features/dashboard/dashboard.tsx"));
const initial = renderToStaticMarkup(React.createElement(Dashboard));
assert(!initial.includes("Your study workspace starts here"), "Dashboard must replace the foundation preview");
assert(initial.includes('role="status"'), "Initial dashboard load must use a page-level data loading state");
const { DashboardView } = load(path.join(src, "features/dashboard/dashboard-view.tsx"));
const data = {
  date: "2026-10-07", timezone: "Asia/Manila", generated_at: "2026-10-07T00:00:00Z",
  today_events: [], upcoming_tasks: [], continue_video_subject_id: "afar-id",
  recall_summary: { overdue: 2, due_today: 3 },
  video_summary: { total_videos: 6, completed_videos: 3, remaining_videos: 3, total_duration_seconds: 210,
    completed_duration_seconds: 100, remaining_duration_seconds: 110, unknown_duration_videos: 1 },
  subjects: [{ id: "far-id", code: "FAR", name: "Financial Accounting and Reporting", display_order: 1,
    color_key: "blue", topic_count: 3, video_count: 4, completed_video_count: 2 },
    { id: "afar-id", code: "AFAR", name: "Advanced Financial Accounting and Reporting", display_order: 2,
      color_key: "indigo", topic_count: 2, video_count: 2, completed_video_count: 1 }],
};
function render(next = data, extra = {}) {
  return renderToStaticMarkup(React.createElement(DashboardView, { data: next, refreshing: false, error: null, onRefresh: () => {}, ...extra }));
}
const empty = render();
assert(empty.includes('aria-label="Study overview"'));
assert(empty.indexOf('id="dashboard-now"') < empty.indexOf('id="dashboard-today"'), "Now/Next is the first study action");
assert(empty.indexOf('aria-label="Study overview"') > empty.indexOf('id="dashboard-today"'), "Today and attention precede progress");
assert(empty.includes("Your schedule is clear") && empty.includes("No pending tasks"));
assert(empty.indexOf('id="dashboard-today"') < empty.indexOf('id="dashboard-tasks"'));
assert(empty.indexOf('id="dashboard-tasks"') < empty.indexOf('id="dashboard-videos"'));
assert(empty.indexOf('id="dashboard-recall"') < empty.indexOf('id="dashboard-tasks"'), "Due recall leads attention items");
assert(empty.includes('href="/recall"') && empty.includes('2 overdue') && empty.includes('3 due today'));
for (const id of ["far-id", "afar-id"]) {
  assert(empty.includes(`href="/subjects/${id}"`));
  assert(empty.includes(`href="/subjects/${id}/videos"`));
}
assert(empty.includes("3 topics"));
assert.match(empty, /<progress value="2" max="4" aria-label="FAR videos completed"/, "Subject meter must show provided completed and total video counts");
assert(empty.includes("1:40") && empty.includes("1:50"), "Lecture time must format backend known totals");
assert(empty.includes("1 video without a duration"));
assert(empty.includes('href="/subjects/afar-id/videos"') && empty.includes("Continue Videos"));
assert(!empty.includes("%"), "Dashboard must not invent a composite percentage");
const populated = render({ ...data, today_events: [{ id: "event-id", occurrence_date: "2026-10-07", is_recurring: true,
  start_at: "2026-10-07T01:00:00Z", end_at: "2026-10-07T02:00:00Z", title: "A real planned event",
  subject_code: "FAR", subject_id: "far-id", topic_title: "A curriculum title", status: "completed" }],
  upcoming_tasks: [{ id: "task-id", title: "A pending task", due_at: "2026-10-06T23:00:00Z", estimated_minutes: 20,
    subject_code: "AFAR", topic_title: null, status: "pending" }] });
assert(populated.includes("09:00") && populated.includes("10:00"), "Event times must use the profile timezone");
assert(populated.includes("A curriculum title") && populated.includes("Completed") && populated.includes("Repeats"));
assert(populated.includes("A pending task") && populated.includes("Overdue"));
assert(!populated.includes("No pending tasks") && !populated.includes("Your schedule is clear"));
const futureTask = render({ ...data, upcoming_tasks: [{ id: "future-task", title: "Next year task", due_at: "2027-10-07T01:00:00Z", status: "pending" }] });
assert(/<time dateTime="2027-10-07T01:00:00Z">[^<]*2027/.test(futureTask), "Task deadlines must distinguish different years");
assert(render(data, { refreshing: true }).includes("3 topics"), "Background dashboard refresh must retain loaded data");
assert(render(data, { error: "Service unavailable" }).includes("3 topics"), "Refresh error must retain loaded data");
const failure = render(null, { error: "Service unavailable" });
assert(!failure.includes('aria-label="Study overview"'), "Unavailable dashboard data must not render zero summary cards");
assert(failure.includes('role="alert"') && !failure.includes("Videos completed"), "Unavailable data must not display invented zero metrics");
const completed = render({ ...data, continue_video_subject_id: null });
assert(completed.includes("Browse Videos") && !completed.includes("Continue Videos"));
console.log("PASS: dashboard loading/empty/error/refresh, timezone/status, real count/time rendering, and implemented-route links");

const noLectures = render({ ...data, video_summary: { total_videos: 0, completed_videos: 0, remaining_videos: 0, completed_duration_seconds: 0, remaining_duration_seconds: 0, unknown_duration_videos: 0 }, subjects: [] });
assert(!/<progress[^>]+aria-label="Lectures completed"/.test(noLectures), "Unavailable lecture total must not show a fabricated progress bar");

// Supplemental panels use existing persisted API values, never placeholder activity.
assert(empty.includes("Unavailable") && empty.includes("Session unavailable"));
assert(!empty.includes("No active session"), "A failed/missing Focus response must not imply an idle session");
const focus = { timezone: "Asia/Manila", server_now: data.generated_at, active_session: null, today_seconds: 3660, today_session_count: 2, recent_sessions: [] };
const activity = { timezone: data.timezone, start_date: "2026-10-01", end_date: data.date,
  summary: { total_seconds: 3660 }, daily: Array.from({ length: 7 }, (_, index) => ({ date: `2026-10-0${index + 1}`, duration_seconds: index === 6 ? 3660 : 0, session_count: index === 6 ? 2 : 0 })) };
const overview = render(data, { extras: { focus, activity, assessments: [{ id: "assessment-a", title: "Real assessment", scheduled_at: null }] } });
assert(overview.includes("1h 01m") && overview.includes("No active session"));
assert(overview.includes("Real assessment") && overview.includes("No date set") && overview.includes('href="/assessments/assessment-a"'));
assert.equal((overview.match(/--day-height:0%/g) || []).length, 6, "Six zero days must retain zero-height bars");
assert.equal((overview.match(/class="desk-day-track"/g) || []).length, 7);
assert(overview.includes('class="study-docket"') && overview.includes('class="desk-day-grid"') && !overview.includes('class="summary-strip'), "Composition is no longer a row of equal metric cards");
for (const href of ["/focus", "/study-plan", "/recall", "/quizzes", "/library"]) assert(overview.includes(`href="${href}"`));
const activeFocus = render(data, { extras: { focus: { ...focus, active_session: { subject_id: "far-id", activity_type: "reading" } }, activity, assessments: [] }, elapsed: 3723 });
assert(activeFocus.includes("01:02:03") && activeFocus.includes("Return to session") && activeFocus.includes("FAR / reading"));
const zeroActivity = render(data, { extras: { focus: { ...focus, today_seconds: 0 }, activity: { ...activity, summary: { total_seconds: 0 }, daily: activity.daily.map((day) => ({ ...day, duration_seconds: 0 })) }, assessments: [] } });
assert.equal((zeroActivity.match(/--day-height:0%/g) || []).length, 7, "Empty activity uses only subdued baselines");
assert(zeroActivity.includes("0h 00m") && zeroActivity.includes("No planned assessments"));
const refreshingPanels = render(data, { refreshing: true, extrasLoading: true, extras: { focus, activity, assessments: [] }, extraErrors: ["Focus"] });
assert(refreshingPanels.includes("1h 01m") && refreshingPanels.includes("could not refresh"), "Background panel refresh retains recorded values");
assert(render(data, { extrasLoading: true }).includes("Loading session"));
const dates = render(data, { extras: { focus, activity, assessments: [
  { id: "past", title: "Past assessment", scheduled_at: "2026-01-01T00:00:00Z" },
  { id: "future", title: "Future assessment", scheduled_at: "2027-01-01T00:00:00Z" },
] } });
assert(dates.includes("Future assessment") && !dates.includes("Past assessment"), "Future dated definitions take priority over overdue definitions");
console.log("PASS: asymmetric composition, recorded Focus time/active session, seven-day zero baselines, assessment links, partial failures and background refresh");


const nextBlock = render({ ...data, today_events: [{ id: "next-event", start_at: "2026-10-07T01:00:00Z", end_at: "2026-10-07T02:00:00Z", status: "scheduled", title: "Next real lecture", subject_code: "FAR", subject_id: "far-id", topic_title: "Revenue", event_type: "lecture", occurrence_date: "2026-10-07" }] });
assert(nextBlock.includes('href="/focus?study_event_id=next-event&amp;occurrence_date=2026-10-07"'), "Scheduled Focus action retains recurring occurrence context");
assert(nextBlock.indexOf("Next real lecture") < nextBlock.indexOf('id="dashboard-today"'));
console.log("PASS: approved docket/agenda/attention/progress hierarchy and contextual scheduled Focus link");
