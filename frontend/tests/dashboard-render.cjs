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
  vm.runInNewContext(code, { module: output, exports: output.exports, require: requireLocal, Error, Intl, Date });
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
assert(empty.indexOf('aria-label="Study overview"') < empty.indexOf('id="dashboard-today"'), "Real-data summaries precede the detailed study plan");
assert(empty.includes("No study events today") && empty.includes("No pending tasks"));
assert(empty.indexOf('id="dashboard-today"') < empty.indexOf('id="dashboard-tasks"'));
assert(empty.indexOf('id="dashboard-tasks"') < empty.indexOf('id="dashboard-videos"'));
assert(empty.indexOf('id="dashboard-tasks"') < empty.indexOf('id="dashboard-recall"'));
assert(empty.includes('href="/recall"') && empty.includes('2 overdue') && empty.includes('3 due today'));
for (const id of ["far-id", "afar-id"]) {
  assert(empty.includes(`href="/subjects/${id}"`));
  assert(empty.includes(`href="/subjects/${id}/videos"`));
}
assert(empty.includes("3 topics") && empty.includes("2 / 4 videos completed"));
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
assert(!populated.includes("No pending tasks") && !populated.includes("No study events today"));
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
