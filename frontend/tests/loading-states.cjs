// Presentation regressions: slow/refailed reads must retain successful content.
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const React = require('react'), ts = require('typescript');
const { renderToStaticMarkup } = require('react-dom/server');
const src = path.join(__dirname, '../src'), cache = new Map();
let readIndex = 0, reads = [];
let mutationMode = false, saves = 0;
function load(file) {
  if (cache.has(file)) return cache.get(file).exports;
  const module = { exports: {} }; cache.set(file, module);
  function local(name) {
    if (name === 'react') return { ...React, useState: value => mutationMode ? [typeof value === 'function' ? value() : value, () => {}] : React.useState(value), useRef: value => mutationMode ? { current: value } : React.useRef(value), useEffect: effect => mutationMode ? undefined : React.useEffect(effect), useCallback: (fn, deps) => mutationMode ? fn : React.useCallback(fn, deps) };
    if (name === '@/services/flashcards') return { updateDeck: () => { saves++; return new Promise(() => {}); }, flashcardError: () => 'Save failed' };
    if (name === './use-study-time-load') return { useStudyTimeLoad: () => reads[readIndex++] };
    if (name === 'next/navigation') return { useRouter: () => ({ push() {} }) };
    if (name === 'next/link') return { default: ({ children, ...props }) => React.createElement('a', props, children) };
    if (name === '@/services/api' || name === './api') return { ApiError: class extends Error {} };
    if (name.startsWith('@/') || name.startsWith('.')) {
      const base = name.startsWith('@/') ? path.join(src, name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(base + (fs.existsSync(base + '.tsx') ? '.tsx' : '.ts'));
    }
    return require(name);
  }
  const code = ts.transpileModule(fs.readFileSync(file, 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  vm.runInNewContext(code, { module, exports: module.exports, require: local, Date, Intl, Error, URLSearchParams });
  return module.exports;
}
const { LoadNotice } = load(path.join(src, 'features/quizzes/shared.tsx'));
const render = props => renderToStaticMarkup(React.createElement(LoadNotice, { error: null, retry() {}, ...props }));
assert.match(render({ loading: true, hasData: false, label: 'Loading questions…' }), /content-skeleton/, 'Cold reads show structured skeletons');
const refreshing = render({ loading: true, hasData: true });
assert.match(refreshing, /Refreshing/);
assert.doesNotMatch(refreshing, /content-skeleton/, 'Background reads do not introduce replacement skeletons');
const failed = render({ loading: false, hasData: true, error: 'Connection unavailable' });
assert.match(failed, /last loaded/i);
assert.match(failed, /Try again/);
assert.equal(render({ loading: false, hasData: true }), '');
console.log('PASS: initial skeletons, compact refresh status and retained-data retry notices');
const { AnalyticsPage } = load(path.join(src, 'features/analytics/analytics-page.tsx'));
const prior = { key: JSON.stringify({ period: 30 }), data: {
  timezone: 'UTC', start_date: '2026-09-01', end_date: '2026-09-30',
  summary: { total_seconds: 3600, session_count: 1, active_days: 1, average_session_seconds: 3600, longest_session_seconds: 3600, planned_seconds: 7200 },
  daily: [{ date: '2026-09-30', duration_seconds: 3600, session_count: 1 }], subjects: [], activities: [],
} };
for (const error of [null, 'Range request failed']) {
  readIndex = 0;
  reads = [{ data: prior, loading: !error, error, retry() {} }, { data: { key: prior.key, offset: 0, data: { sessions: [], total: 0 } }, loading: !error, error, retry() {} }];
  const html = renderToStaticMarkup(React.createElement(AnalyticsPage));
  assert.match(html, /1:00:00/, 'Previous real totals stay visible while another range loads or fails');
  assert.match(html, /Daily study time/);
  assert.doesNotMatch(html, /content-skeleton/, 'Retained charts are never replaced by initial skeletons');
}
console.log('PASS: analytics retains previous range/chart on slow and failed range requests');
mutationMode = true;
const { DeckEditor } = load(path.join(src, 'features/flashcards/deck-editor.tsx'));
const tree = DeckEditor({ deck: { id: 'temporary-render-fixture', title: 'Study deck' }, close() {}, saved() {} });
function find(node, type) { if (!node || typeof node !== 'object') return null; if (node.type === type) return node; return React.Children.toArray(node.props?.children).map(child => find(child, type)).find(Boolean); }
const form = find(tree, 'form');
form.props.onSubmit({ preventDefault() {} }); form.props.onSubmit({ preventDefault() {} });
assert.equal(saves, 1, 'Rapid submissions before React rerenders start only one request');
console.log('PASS: rapid save submissions are synchronously guarded');
