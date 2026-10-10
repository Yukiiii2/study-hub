const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
const React = require("react"), { renderToStaticMarkup } = require("react-dom/server"), ts = require("typescript");
const src = path.join(__dirname, "../src"), modules = new Map(), calls = [];
let harness = null, post = async () => ({ id: "saved-id" });
class ApiError extends Error { constructor(message, status) { super(message); this.status = status; } }
const api = { ApiError, authenticatedPost: async (...args) => { calls.push(args); return post(...args); }, authenticatedGet: async () => ({}), authenticatedPatch: async () => ({}) };
const shim = { ...React,
  useState(initial) { if (!harness) return React.useState(initial); const index = harness.index++; if (!(index in harness.values)) harness.values[index] = typeof initial === "function" ? initial() : initial; const owner = harness; return [owner.values[index], (value) => { owner.values[index] = typeof value === "function" ? value(owner.values[index]) : value; }]; },
  useRef(initial) { if (!harness) return React.useRef(initial); const index = harness.index++; if (!(index in harness.values)) harness.values[index] = { current: initial }; return harness.values[index]; },
  useCallback(callback, dependencies) { return harness ? callback : React.useCallback(callback, dependencies); },
  useEffect(callback, dependencies) { if (!harness) React.useEffect(callback, dependencies); },
};
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  function local(name) {
    if (name === "react") return shim;
    if (name === "next/link") return { default: ({ children, ...props }) => React.createElement("a", props, children) };
    if (name === "@/features/auth/auth-provider") return { useAuth: () => ({ user: { id: "owner" } }) };
    if (name === "@/services/api" || name === "./api") return api;
    if (name === "@/features/quizzes/shared") return { ...load(path.join(src, "features/quizzes/shared.tsx")), useQuizLoad: () => ({ data: { resources: [], total: 0 }, loading: false, error: null, retry() {} }) };
    if (name.startsWith("@/") || name.startsWith(".")) { const base = name.startsWith("@/") ? path.join(src, name.slice(2)) : path.resolve(path.dirname(file), name); return load(fs.existsSync(base + ".tsx") ? base + ".tsx" : base + ".ts"); }
    return require(name);
  }
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  vm.runInNewContext(code, { module: output, exports: output.exports, require: local, AbortController, URLSearchParams, Date, Error });
  return output.exports;
}
const ai = load(path.join(src, "services/ai.ts"));
const state = load(path.join(src, "features/assistant/draft-state.ts"));
const saveState = load(path.join(src, "features/assistant/draft-save.ts"));
const { AIResponseView } = load(path.join(src, "features/assistant/response-view.tsx"));
const { AIDraftPreview } = load(path.join(src, "features/assistant/draft-preview.tsx"));
const { AssistantWorkspace } = load(path.join(src, "features/assistant/assistant-page.tsx"));
const { QuestionEditor } = load(path.join(src, "features/quizzes/question-editor.tsx"));
const { CardEditor } = load(path.join(src, "features/flashcards/card-editor.tsx"));
const { ExplainAnswerAction } = load(path.join(src, "features/assistant/explain-answer.tsx"));
const metadata = { provider: "synthetic", model: "fixture", generated_at: "2026-10-09T00:00:00Z", context: { resource_id: "source" }, grounding: "resource", notice: null, insufficient_context: false, citations: [{ resource_id: "source", resource_title: "Text <notes>", page_number: 2, quote: "Source <script>quote</script>" }] };
const question = { question_type: "single_select", prompt: "Draft <question>", explanation: "Reason", options: [{ key: "A", text: "Correct" }, { key: "B", text: "Wrong" }], correct_keys: ["A"], subject_id: null, topic_id: null, resource_id: "source", source_page: 2, ai_draft_receipt: "private-receipt" };
const card = { front: "Draft front", back: "Draft back", status: "suspended", notes: null, deck_id: null, subject_id: null, topic_id: null, resource_id: null, source_page: null, ai_draft_receipt: "card-receipt" };
const questions = { ...metadata, questions: [question] };
const render = (component, props) => renderToStaticMarkup(React.createElement(component, props));
const answer = render(AIResponseView, { response: { ...metadata, answer: "Answer <img onerror=alert(1)>" } });
assert(answer.includes("&lt;img") && answer.includes("&lt;script&gt;quote&lt;/script&gt;") && answer.includes('href="/library/source"') && answer.includes("Page 2"));
assert(!answer.includes("<script>") && !answer.includes("<img"));
assert(render(AIResponseView, { response: { ...metadata, grounding: "topic_context", citations: [], answer: "Concept" } }).includes("No uploaded source supports"));
assert(render(AIResponseView, { response: { ...metadata, provider: null, model: null, grounding: "none", citations: [], insufficient_context: true, answer: "" } }).includes("not enough relevant context"));
const preview = render(AIDraftPreview, { response: questions });
assert(preview.includes("Review, edit and save") && preview.includes("Remove draft") && preview.includes("Nothing is saved automatically"));
assert(!preview.includes("private-receipt"));
assert.equal(calls.length, 0, "Rendering a preview must never persist material");
assert.equal(state.retainDraftPreview(questions, { ...metadata, questions: [], insufficient_context: true }), questions);
assert.equal(saveState.aiCardSaveOutcomeUnknown(new ApiError("invalid", 422)), false);
assert.equal(saveState.aiCardSaveOutcomeUnknown(new ApiError("lost confirmation", 502)), true);
assert.equal(saveState.aiCardSaveOutcomeUnknown(new Error("offline")), true);
const gate = new state.AIRequestGate(), ticket = gate.begin(); assert.equal(gate.begin(), null); gate.invalidate(); assert.equal(gate.current(ticket), false); assert.notEqual(gate.begin(), null);
function tree(component, props, store = { values: [], index: 0 }) { harness = store; store.index = 0; try { return { node: component(props), store }; } finally { harness = null; } }
function find(node, predicate) { if (!node) return null; if (Array.isArray(node)) { for (const child of node) { const match = find(child, predicate); if (match) return match; } return null; } if (typeof node !== "object") return null; if (predicate(node)) return node; return find(node.props?.children, predicate); }
const tick = () => new Promise((resolve) => setImmediate(resolve));
(async () => {
  await ai.explainAIAnswer({ attempt_id: "attempt", question_id: "question" });
  assert.equal(calls.at(-1)[0], "/api/ai/explain-answer"); assert.equal(JSON.stringify(calls.at(-1)[1]), '{"attempt_id":"attempt","question_id":"question"}');
  calls.length = 0;
  let resolveGeneration; post = () => new Promise((resolve) => { resolveGeneration = resolve; });
  const workspace = tree(AssistantWorkspace, { initial: { subject_id: "11111111-1111-4111-8111-111111111111", mode: "quiz" } });
  const form = find(workspace.node, (node) => node.type === "form");
  form.props.onSubmit({ preventDefault() {} }); form.props.onSubmit({ preventDefault() {} });
  assert.equal(calls.length, 1, "Only one generation may be in flight");
  assert.equal(calls[0][0], "/api/ai/generate-quiz");
  resolveGeneration(questions); await tick();
  let rendered = tree(AssistantWorkspace, { initial: {} }, workspace.store);
  assert(find(rendered.node, (node) => node.type === AIDraftPreview), "Successful generation creates only an editable preview");
  assert.equal(calls.length, 1, "Generation never calls persistence endpoints");
  post = async () => { throw new ApiError("provider-secret", 503); };
  find(rendered.node, (node) => node.type === "form").props.onSubmit({ preventDefault() {} }); await tick();
  rendered = tree(AssistantWorkspace, { initial: {} }, workspace.store);
  assert(find(rendered.node, (node) => node.type === AIDraftPreview), "Transient errors preserve current preview");
  assert(!JSON.stringify(rendered.node).includes("provider-secret"));
  calls.length = 0; post = async () => ({ id: "confirmed-question" });
  const questionEditor = tree(QuestionEditor, { initial: question, close() {}, saved() {} });
  const questionForm = find(questionEditor.node, (node) => node.type === "form");
  questionForm.props.onSubmit({ preventDefault() {} }); questionForm.props.onSubmit({ preventDefault() {} }); await tick();
  assert.equal(calls.length, 1, "Double confirmation must send only one save");
  assert.equal(calls[0][0], "/api/questions"); assert.equal(calls[0][1].ai_draft_receipt, question.ai_draft_receipt);
  calls.length = 0;
  const cardEditor = tree(CardEditor, { initial: { ...card, status: "active" }, close() {}, saved() {} });
  find(cardEditor.node, (node) => node.type === "form").props.onSubmit({ preventDefault() {} }); await tick();
  assert.equal(calls[0][0], "/api/flashcards"); assert.equal(calls[0][1].status, "suspended"); assert.equal(calls[0][1].ai_draft_receipt, card.ai_draft_receipt);
  calls.length = 0; post = async () => { throw new ApiError("unavailable", 503); };
  let uncertain = 0;
  const uncertainEditor = tree(CardEditor, { initial: card, close() {}, saved() {}, uncertain() { uncertain++; } });
  const uncertainForm = find(uncertainEditor.node, (node) => node.type === "form");
  uncertainForm.props.onSubmit({ preventDefault() {} }); await tick();
  uncertainForm.props.onSubmit({ preventDefault() {} }); await tick();
  assert.equal(calls.length, 1, "A lost AI-card save confirmation must block repeated POSTs"); assert.equal(uncertain, 1);
  const unknownView = tree(CardEditor, { initial: card, close() {}, saved() {} }, uncertainEditor.store);
  assert(find(unknownView.node, (node) => node.type === "button" && node.props.children === "Confirm and save flashcard").props.disabled);
  post = async () => ({ id: "confirmed" });
  calls.length = 0;
  const draftView = tree(AIDraftPreview, { response: questions });
  find(draftView.node, (node) => node.type === "button" && node.props.children === "Remove draft").props.onClick();
  assert(!find(tree(AIDraftPreview, { response: questions }, draftView.store).node, (node) => node.type === "button" && node.props.children === "Review, edit and save"));
  assert.equal(calls.length, 0, "Removing a draft never calls save/delete APIs");
  const explanation = tree(ExplainAnswerAction, { attemptId: "completed-attempt", questionId: "snapshot-question" });
  find(explanation.node, (node) => node.type === "button").props.onClick(); await tick();
  assert.equal(Object.keys(calls[0][1]).sort().join(","), "attempt_id,question_id", "Explanation must send only canonical snapshot IDs");
  console.log("PASS: AI API intents, source escaping, bounded one-flight generation, retained drafts, explicit per-item save, receipt preservation and suspended AI cards");
})().catch((error) => { console.error(error); process.exitCode = 1; });
