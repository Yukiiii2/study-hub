// Focused recurrence/UI boundary checks; never populate application data.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ts = require("typescript");
const source = fs.readFileSync(path.join(__dirname, "../src/features/study-plan/dates.ts"), "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017 } }).outputText;
const output = { exports: {} };
vm.runInNewContext(compiled, { module: output, exports: output.exports, Intl, Date, Set, Error });
const dates = output.exports;
assert.equal(dates.localToInstant("2026-10-06", "09:00", "Asia/Taipei"), "2026-10-06T01:00:00.000Z");
assert.equal(dates.localToInstant("2026-10-06", "09:00", "Asia/Kathmandu"), "2026-10-06T03:15:00.000Z");
assert.throws(() => dates.localToInstant("2026-03-08", "02:30", "America/New_York"), /does not exist/);
assert.throws(() => dates.localToInstant("2026-11-01", "01:30", "America/New_York"), /occurs twice/);
assert.throws(() => dates.localToInstant("2026-02-30", "09:00", "UTC"), /valid date/);
assert.equal(dates.dateAdd("2026-12-31", 1), "2027-01-01");
assert.equal(dates.calendarDays("2026-10-06", "month").length, 42);
assert.equal(dates.calendarDays("2026-10-06", "week")[0], "2026-10-05");
console.log("PASS: 8 planner timezone/date boundary checks");
assert.equal(typeof dates.compactMonthDays, "function", "Compact month uses its own Sunday-first date presentation");
for (const [date, first, length] of [["2026-10-15", "2026-09-27", 35], ["2026-08-01", "2026-07-26", 42], ["2026-02-01", "2026-02-01", 35], ["2024-02-29", "2024-01-28", 35]]) {
  const days = dates.compactMonthDays(date);
  assert.equal(days[0], first); assert.equal(days.length, length);
  assert.equal(new Set(days).size, length);
  assert.equal(dates.weekday(days[0]), 0); assert.equal(dates.weekday(days.at(-1)), 6);
  const last = new Date(`${date.slice(0,7)}-01T12:00:00Z`); last.setUTCMonth(last.getUTCMonth()+1); last.setUTCDate(0);
  assert(days.includes(last.toISOString().slice(0,10)), "The last day of the real month is present");
}
console.log("PASS: Sunday-first 5/6-week compact months, year/leap boundaries, desktop dates unchanged");
