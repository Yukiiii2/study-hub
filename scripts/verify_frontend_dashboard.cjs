// Explicit read-only comparison of actual frontend dashboard/curriculum/planner modules.
// Existing ignored verification credentials stay in memory; no private payload is saved.
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "..");
const frontend = path.join(root, "frontend");
const ts = require(path.join(frontend, "node_modules/typescript"));
const React = require(path.join(frontend, "node_modules/react"));
const { renderToStaticMarkup } = require(path.join(frontend, "node_modules/react-dom/server"));
const { loadEnvConfig } = require(path.join(frontend, "node_modules/@next/env"));
const publicEnv = { ...loadEnvConfig(frontend, false, undefined, true).combinedEnv };
const privateEnv = { ...loadEnvConfig(path.join(root, "backend"), false, undefined, true).combinedEnv };
const browserEnv = Object.fromEntries(Object.entries(publicEnv).filter(([key]) => key.startsWith("NEXT_PUBLIC_")));
const modules = new Map();
let stage = "environment and sign-in";
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  const localRequire = (name) => {
    if (name === "next/link") return { default: ({ children, ...props }) => React.createElement("a", props, children) };
    if (name.startsWith("@/") || name.startsWith(".")) {
      const base = name.startsWith("@/") ? path.join(frontend, "src", name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(fs.existsSync(base + ".tsx") ? base + ".tsx" : base + ".ts");
    }
    return require(path.join(frontend, "node_modules", name));
  };
  const originFetch = async (url, options = {}) => {
    const response = await fetch(url, { ...options, headers: { ...options.headers, Origin: "http://localhost:3001" } });
    assert.equal(response.headers.get("access-control-allow-origin"), "http://localhost:3001", "Backend CORS must allow the frontend");
    return response;
  };
  vm.runInNewContext(code, { module: output, exports: output.exports, require: localRequire,
    process: { env: browserEnv }, fetch: originFetch, AbortController, URLSearchParams, Error, Promise, Intl, Date, Map }, { filename: file });
  return output.exports;
}
(async () => {
  assert.equal(browserEnv.NEXT_PUBLIC_API_URL, "http://localhost:8001");
  assert(privateEnv.PHASE2_VERIFY_EMAIL && privateEnv.PHASE2_VERIFY_PASSWORD, "Existing local verification credentials required");
  const auth = load(path.join(frontend, "src/features/auth/supabase.ts")).getSupabaseBrowserClient();
  const api = load(path.join(frontend, "src/services/api.ts"));
  const dashboard = load(path.join(frontend, "src/services/dashboard.ts"));
  const subjects = load(path.join(frontend, "src/services/subjects.ts"));
  const videos = load(path.join(frontend, "src/services/videos.ts"));
  const planner = load(path.join(frontend, "src/services/study-plan.ts"));
  const dates = load(path.join(frontend, "src/features/study-plan/dates.ts"));
  try {
    await assert.rejects(() => dashboard.getDashboard(), (error) => error.status === 401);
    const anon = await fetch(`${browserEnv.NEXT_PUBLIC_API_URL}/api/dashboard`);
    assert.equal(anon.status, 401);
    const login = await auth.auth.signInWithPassword({ email: privateEnv.PHASE2_VERIFY_EMAIL, password: privateEnv.PHASE2_VERIFY_PASSWORD });
    assert(!login.error && login.data.session, "SDK sign-in failed");
    const me = await api.authenticatedGet("/api/auth/me"); assert.equal(me.id, login.data.user.id);
    stage = "dashboard and curriculum comparison";
    const data = await dashboard.getDashboard();
    const existing = await subjects.getSubjects();
    assert.deepEqual(data.subjects.map((s) => s.id), existing.map((s) => s.id));
    assert.deepEqual([...data.subjects.map((s) => s.code)].sort(), ["AFAR", "AP", "AT", "FAR", "MAS", "RFBT", "TAX"]);
    const sums = { total_videos: 0, completed_videos: 0, total_duration_seconds: 0, completed_duration_seconds: 0,
      remaining_duration_seconds: 0, unknown_duration_videos: 0 };
    let totalTopics = 0;
    const inProgress = [], unfinished = [];
    for (const subject of data.subjects) {
      const [topics, lectures] = await Promise.all([subjects.getSubjectTopics(subject.id), videos.getSubjectVideos(subject.id)]);
      assert.equal(subject.topic_count, topics.length); totalTopics += topics.length;
      assert.equal(subject.video_count, lectures.summary.total_videos);
      assert.equal(subject.completed_video_count, lectures.summary.completed_videos);
      for (const key of Object.keys(sums)) sums[key] += lectures.summary[key];
      if (lectures.videos.some((v) => v.status === "in_progress")) inProgress.push(subject.id);
      if (lectures.summary.completed_videos < lectures.summary.total_videos) unfinished.push(subject.id);
      console.log(`PASS: ${subject.code} topic/video/completion counts match existing PostgreSQL-backed APIs`);
    }
    for (const [key, count] of Object.entries(sums)) assert.equal(data.video_summary[key], count);
    assert.equal(data.video_summary.remaining_videos, sums.total_videos - sums.completed_videos);
    assert.equal(data.continue_video_subject_id, inProgress[0] ?? unfinished[0] ?? null);
    stage = "planner comparison";
    const context = await planner.getPlannerContext(); assert.equal(data.timezone, context.timezone);
    const start = dates.localToInstant(data.date, "00:00", data.timezone);
    const end = dates.localToInstant(dates.dateAdd(data.date, 1), "00:00", data.timezone);
    const events = await planner.getEvents(start, end);
    const eventKey = (event) => `${event.id}/${event.occurrence_date ?? "one"}/${event.start_at}/${event.end_at}/${event.status}`;
    assert.deepEqual(data.today_events.map(eventKey), events.map(eventKey));
    const tasks = (await planner.getTasks()).filter((task) => task.status === "pending").sort((a, b) => {
      if (a.due_at === null && b.due_at !== null) return 1;
      if (b.due_at === null && a.due_at !== null) return -1;
      return (a.due_at && b.due_at ? new Date(a.due_at) - new Date(b.due_at) || a.due_at.localeCompare(b.due_at) : 0)
        || a.created_at.localeCompare(b.created_at) || a.id.localeCompare(b.id);
    }).slice(0, 5);
    assert.deepEqual(data.upcoming_tasks.map((task) => task.id), tasks.map((task) => task.id));
    console.log("PASS: profile timezone, today's real occurrences, and pending task due ordering match planner APIs");
    stage = "authenticated dashboard rendering";
    const { DashboardView } = load(path.join(frontend, "src/features/dashboard/dashboard-view.tsx"));
    const html = renderToStaticMarkup(React.createElement(DashboardView, { data, refreshing: false, error: null, onRefresh: () => {} }));
    for (const subject of data.subjects) {
      assert(html.includes(`href="/subjects/${subject.id}"`));
      assert(html.includes(`href="/subjects/${subject.id}/videos"`));
    }
    assert.equal(html.includes("No study events today"), data.today_events.length === 0);
    assert.equal(html.includes("No pending tasks"), data.upcoming_tasks.length === 0);
    assert(!html.includes("Study tools are not available yet") && !html.includes("%"));
    console.log(`PASS: authenticated frontend dashboard renders ${data.subjects.length} real subjects, ${totalTopics} topics, ${sums.total_videos} videos; known durations/counts match`);
    stage = "frontend routes";
    for (const route of ["/", "/subjects", "/study-plan", `/subjects/${data.subjects[0].id}`, `/subjects/${data.subjects[0].id}/videos`]) {
      assert.equal((await fetch(`http://localhost:3001${route}`)).status, 200);
    }
    console.log("PASS: Dashboard, Subjects, Study Plan, subject detail and Videos routes respond on port 3001");
  } finally {
    await auth.auth.signOut({ scope: "local" }); auth.auth.stopAutoRefresh();
  }
})().catch(() => { console.error(`Dashboard verification failed during ${stage}; no credential or private payload details printed.`); process.exitCode = 1; });
