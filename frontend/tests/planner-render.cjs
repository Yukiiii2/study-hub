// Render the actual planner's loading, failure and empty states without API writes.
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const React = require("react"), ts = require("typescript");
const { renderToStaticMarkup } = require("react-dom/server");
const src = path.join(__dirname, "../src"), modules = new Map();
let states, stateIndex;
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const module = { exports: {} }; modules.set(file, module);
  const local = (name) => {
    if (name === "react") return { ...React, useEffect: () => {}, useState: () => [states[stateIndex++], () => {}] };
    if (name === "@/services/api" || name === "./api") return { ApiError: class extends Error {} };
    if (name.startsWith("@/") || name.startsWith(".")) {
      const base = name.startsWith("@/") ? path.join(src, name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(fs.existsSync(base + ".tsx") ? base + ".tsx" : base + ".ts");
    }
    return require(name);
  };
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, require: local, Date, Intl, Error });
  return module.exports;
}
const { StudyPlanner } = load(path.join(src, "features/study-plan/study-planner.tsx"));
function render({ initial = false, eventLoading = false, eventError = null, error = null, tab = "calendar" } = {}) {
  states = [initial ? null : { timezone: "UTC", active_session: null }, [], [], [], tab, "month", "2026-10-10", 0, error, eventError, null, null, initial, eventLoading, false, null];
  stateIndex = 0;
  return renderToStaticMarkup(React.createElement(StudyPlanner));
}
const initial = render({ initial: true });
assert(initial.includes("Loading planner") && !initial.includes('aria-label="Planning overview"'));
assert(!render({ error: "Unavailable" }).includes('aria-label="Planning overview"'));
const empty = render();
assert(empty.includes('aria-label="Planning overview"') && empty.includes("Record actual study time"));
for (const control of ["New event", "Start session", "Previous month", "Next month", "Month", "Week"]) assert(empty.includes(control), control);
assert(empty.includes("No events in this period"));
for (const options of [{ eventLoading: true }, { eventError: "Unavailable" }]) {
  const html = render(options);
  assert(/Events in view<\/span><\/dt><dd><span class="summary-metric-value">—/.test(html), "Unknown event data must not show fabricated zero counts");
}
const tasks = render({ tab: "tasks" });
assert(tasks.includes("New task") && tasks.includes("No study tasks yet") && tasks.includes("Saved study tasks"));
console.log("PASS: planner bootstrap/failure/empty states, unavailable summaries, calendar controls, task view and session actions");
