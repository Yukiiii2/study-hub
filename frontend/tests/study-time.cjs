// Focused timer/date boundary checks and accessible analytics rendering; no live data.
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const ts = require("typescript"), React = require("react"), { renderToStaticMarkup } = require("react-dom/server");
const src = path.join(__dirname, "../src"), modules = new Map();
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const module = { exports: {} }; modules.set(file, module);
  const local = (name) => {
    if (name.startsWith("@/") || name.startsWith(".")) {
      const base = name.startsWith("@/") ? path.join(src, name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(fs.existsSync(base + ".tsx") ? base + ".tsx" : base + ".ts");
    }
    return require(name);
  };
  const compiled = ts.transpileModule(fs.readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  vm.runInNewContext(compiled, { module, exports: module.exports, require: local, Date, Intl, Error });
  return module.exports;
}
const { elapsedSeconds, rangeError, studyDuration } = load(path.join(src, "features/analytics/presentation.ts"));
const { DailyChart, CalendarHeatmap, TimeBar } = load(path.join(src, "features/analytics/analytics-charts.tsx"));
const { focusEventWindow, eventOverlapsFocusDates } = load(path.join(src, "features/focus/event-window.ts"));
const render = (component, props) => renderToStaticMarkup(React.createElement(component, props));
const anchor = { serverTime: Date.parse("2026-10-09T12:10:00Z"), monotonicTime: 500 };
assert.equal(elapsedSeconds("2026-10-09T12:00:00Z", anchor, 1500), 601, "Restore includes server-measured time before the page loaded");
assert.equal(elapsedSeconds("2026-10-09T12:00:00Z", anchor, 65000), 664, "Timer derives from monotonic time across delayed interval ticks");
assert.equal(elapsedSeconds("2026-10-09T12:20:00Z", anchor, 1500), 0, "Never display negative elapsed time");
assert.equal(studyDuration(0), "0:00:00");
assert.equal(studyDuration(90061), "25:01:01", "Long sessions do not wrap at 24 hours");
assert.equal(rangeError("2026-07-12", "2026-10-09", "2026-10-09"), null, "90 inclusive days accepted");
assert.match(rangeError("2026-07-11", "2026-10-09", "2026-10-09"), /at most 90/);
assert.match(rangeError("2026-10-09", "2026-10-10", "2026-10-09"), /future/);
assert.match(rangeError("2026-02-30", "2026-03-01", "2026-10-09"), /valid/);
assert.match(rangeError("", "2026-10-09", "2026-10-09"), /both/);
assert.match(rangeError("2026-10-09", "2026-10-08", "2026-10-09"), /before/);
const daily = [{ date: "2026-10-08", duration_seconds: 0, session_count: 0 }, { date: "2026-10-09", duration_seconds: 90, session_count: 1 }];
const chart = render(DailyChart, { daily });
assert.match(chart, /Daily values/);
assert.match(chart, /0:01:30/);
assert.match(chart, /0:00:00/);
const heatmap = render(CalendarHeatmap, { daily });
assert.match(heatmap, /tabindex="0"/);
assert.match(heatmap, /0:01:30, 1 completed sessions/);
assert.match(heatmap, /data-level="0"/);
assert.match(render(TimeBar, { label: "Actual", seconds: 0, maximum: 0 }), /width:0%/);
assert.doesNotMatch(render(DailyChart, { daily: daily.map((day) => ({ ...day, duration_seconds: 0, session_count: 0 })) }), /NaN|Infinity/);
const event = (start_at, end_at) => ({ start_at, end_at });
// Havana repeats midnight; Santiago skips midnight. Loading a selector must not
// apply strict scheduling-form rules or choose a fabricated local instant.
for (const [today, timezone, savedEvent] of [
  ["2026-11-01", "America/Havana", event("2026-11-01T04:30:00Z", "2026-11-01T05:30:00Z")],
  ["2026-09-06", "America/Santiago", event("2026-09-06T04:00:00Z", "2026-09-06T05:00:00Z")],
]) {
  const stored = JSON.stringify(savedEvent);
  const bounds = focusEventWindow(today);
  assert.ok(Date.parse(bounds.startAt) < Date.parse(savedEvent.start_at));
  assert.ok(Date.parse(bounds.endAt) > Date.parse(savedEvent.end_at));
  assert.equal(eventOverlapsFocusDates(savedEvent, today, bounds.endDate, timezone), true);
  assert.equal(JSON.stringify(savedEvent), stored, "Reading dates preserves saved event timestamps and context");
}
assert.equal(eventOverlapsFocusDates(event("2026-10-08T14:00:00Z", "2026-10-08T16:00:00Z"), "2026-10-09", "2026-10-17", "Asia/Taipei"), false, "An event ending at the first local midnight is excluded");
assert.equal(eventOverlapsFocusDates(event("2026-10-16T16:00:00Z", "2026-10-16T17:00:00Z"), "2026-10-09", "2026-10-17", "Asia/Taipei"), false, "An event starting on the exclusive last date is excluded");
assert.equal(eventOverlapsFocusDates(event("2026-10-08T15:30:00Z", "2026-10-08T16:30:00Z"), "2026-10-09", "2026-10-17", "Asia/Taipei"), true, "A saved event crossing the first local midnight is included");
console.log("PASS: timer restoration, date bounds, midnight-DST event reads and accessible zero/real analytics values");
