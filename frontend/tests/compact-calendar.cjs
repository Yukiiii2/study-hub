const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const ts = require('typescript'), React = require('react'), { renderToStaticMarkup } = require('react-dom/server');
const root = path.join(__dirname, '../src'), modules = new Map(), buttons = [];
const file = path.join(root, 'features/study-plan/compact-calendar.tsx');
assert(fs.existsSync(file), 'The compact calendar must be an implemented production component');
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const module = { exports: {} }; modules.set(file, module);
  const local = name => {
    if (name === 'react/jsx-runtime') {
      const runtime = require(name), capture = fn => (type, props, ...rest) => { if (type === 'button') buttons.push(props); return fn(type, props, ...rest); };
      return { ...runtime, jsx: capture(runtime.jsx), jsxs: capture(runtime.jsxs) };
    }
    if (name.startsWith('@/') || name.startsWith('.')) {
      const base = name.startsWith('@/') ? path.join(root, name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(base + (fs.existsSync(base + '.tsx') ? '.tsx' : '.ts'));
    }
    return require(name);
  };
  const code = ts.transpileModule(fs.readFileSync(file, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, require: local, Date, Intl }); return module.exports;
}
const { CompactCalendar } = load(file);
const { compactMonthDays, calendarDays } = load(path.join(root, 'features/study-plan/dates.ts'));
let selected, added, edited;
const events = [{ id:'event-a', subject_id:'far', title:'Revenue recognition', start_at:'2026-10-15T01:30:00Z', end_at:'2026-10-15T02:30:00Z', status:'scheduled' }];
function render(date='2026-10-15', pending=false, view='month') {
  buttons.length=0;
  return renderToStaticMarkup(React.createElement(CompactCalendar, {
    anchor:'2026-10-15', view, days:view==='month'?compactMonthDays('2026-10-15'):calendarDays('2026-10-15','week'), today:'2026-10-15', selectedDate:date, timezone:'Asia/Manila', pending,
    subjects:[{id:'far',code:'FAR',color_key:'blue'}], eventsForDate:d=>d==='2026-10-15'?events:[], onSelect:d=>{selected=d}, onAdd:d=>{added=d}, onEdit:e=>{edited=e},
  }));
}
const html=render();
assert.equal(buttons.filter(b=>b['data-date']).length,35);
assert.match(html,/Sun<\/span>.*Mon<\/span>.*Sat<\/span>/);
assert.match(html,/09:30/);assert.match(html,/Revenue recognition/);assert.match(html,/FAR/);
assert(!html.split('<section class="compact-day-agenda"')[0].includes('Revenue recognition'),'Titles never appear inside month cells');
assert.match(html,/compact-day-markers/);assert.match(html,/aria-current="date"/);assert.match(html,/aria-pressed="true"/);
buttons.find(b=>b['data-date']==='2026-10-18').onClick();assert.equal(selected,'2026-10-18');
buttons.find(b=>b.className==='compact-agenda-add secondary-button').onClick();assert.equal(added,'2026-10-15');
buttons.find(b=>b.className==='compact-agenda-event').onClick();assert.equal(edited.id,'event-a');
assert.match(render('2026-10-18'),/No study blocks planned/);
buttons.find(b=>b.className==='compact-agenda-add secondary-button').onClick();assert.equal(added,'2026-10-18');
assert.doesNotMatch(render('2026-10-18',true),/No study blocks planned/,'An unresolved range never flashes an empty agenda');
console.log('PASS: compact grid, selected day, real event markers/agenda, target-date actions and pending state');

const week=render('2026-10-15',false,'week');
assert.match(week,/compact-week-strip/);assert.doesNotMatch(week,/compact-month-grid|planner-week-grid/);
assert.equal(buttons.filter(button=>button['data-date']).length,7);
assert.match(week,/09:30/);assert.match(week,/10:30/);
console.log('PASS: mobile Week day strip, selected chronological timeline and full time range');
