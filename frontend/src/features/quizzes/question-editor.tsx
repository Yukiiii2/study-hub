"use client";

import { useRef, useState } from "react";
import { createQuestion, updateQuestion, quizError, type Question, type QuestionInput, type QuestionType } from "@/services/quizzes";
import { Associations, QuizDialog, SourceFields } from "./shared";

export function nextOptionKey(options: { key: string }[]): string | undefined {
  return [..."ABCDEF"].find((key) => !options.some((option) => option.key === key));
}

export function QuestionEditor({ question, initial, close, saved }: { question?: Question; initial?: Partial<QuestionInput>; close: () => void; saved: (question: Question) => void }) {
  const seed = question ?? initial;
  const saveLock = useRef(false);
  const receipt = question ? undefined : initial?.ai_draft_receipt;
  const [type, setType] = useState<QuestionType>(seed?.question_type ?? "single_select");
  const [prompt, setPrompt] = useState(seed?.prompt ?? "");
  const [explanation, setExplanation] = useState(seed?.explanation ?? "");
  const [options, setOptions] = useState(seed?.options ?? [{ key: "A", text: "" }, { key: "B", text: "" }]);
  const [correct, setCorrect] = useState(seed?.correct_keys ?? []);
  const [subject, setSubject] = useState(seed?.subject_id ?? "");
  const [topic, setTopic] = useState(seed?.topic_id ?? "");
  const [resource, setResource] = useState(seed?.resource_id ?? "");
  const [page, setPage] = useState(seed?.source_page?.toString() ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  function chooseType(next: QuestionType) { setType(next); setCorrect([]); setOptions(next === "true_false" ? [{ key: "TRUE", text: "True" }, { key: "FALSE", text: "False" }] : [{ key: "A", text: "" }, { key: "B", text: "" }]); }
  async function save() {
    if (saveLock.current) return;
    if (!prompt.trim() || options.some((item) => !item.text.trim()) || !correct.length) { setError("Enter a question, every option and at least one correct answer."); return; }
    if (new Set(options.map((item) => item.text.trim().toLowerCase())).size !== options.length) { setError("Answer options must have distinct text."); return; }
    const input: QuestionInput = { question_type: type, prompt: prompt.trim(), explanation: explanation.trim() || null, options: options.map((item) => ({ ...item, text: item.text.trim() })), correct_keys: correct, subject_id: subject || null, topic_id: topic || null, resource_id: resource || null, source_page: page ? Number(page) : null };
    if (receipt) input.ai_draft_receipt = receipt;
    saveLock.current = true; setBusy(true); setError(null);
    try { const result = question ? await updateQuestion(question.id, input) : await createQuestion(input); saved(result); close(); }
    catch (failure) { setError(quizError(failure)); }
    finally { saveLock.current = false; setBusy(false); }
  }
  return <QuizDialog title={question ? "Edit question" : receipt ? "Review AI question" : "New question"} close={close} busy={busy}>{receipt && <p className="resource-note">Review the question and source before confirming. Saving adds one question to Question Bank; it does not create a quiz.</p>}<form onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset disabled={busy} className="planner-form-grid">
    <label className="planner-wide">Question type<select value={type} onChange={(event) => chooseType(event.target.value as QuestionType)}><option value="single_select">Single select</option><option value="multi_select">Multi select</option><option value="true_false">True / false</option></select></label>
    <label className="planner-wide">Question<textarea autoFocus required maxLength={5000} rows={4} value={prompt} onChange={(event) => setPrompt(event.target.value)} /></label>
    <fieldset className="quiz-option-editor planner-wide"><legend>Answer options and correct answer{type === "multi_select" ? "s" : ""}</legend>{options.map((option) => <div className="quiz-editor-option" key={option.key}><label className="planner-check"><input type={type === "multi_select" ? "checkbox" : "radio"} name="correct-answer" checked={correct.includes(option.key)} onChange={(event) => setCorrect(type === "multi_select" ? event.target.checked ? [...correct, option.key] : correct.filter((key) => key !== option.key) : [option.key])} aria-label={`Mark ${option.key} correct`} /><span>{option.key}</span></label><label className="quiz-option-text"><span className="quiz-sr-only">Option {option.key} text</span><input required maxLength={1000} readOnly={type === "true_false"} value={option.text} onChange={(event) => setOptions(options.map((item) => item.key === option.key ? { ...item, text: event.target.value } : item))} /></label></div>)}{type !== "true_false" && <div className="resource-actions"><button type="button" className="secondary-button" disabled={!nextOptionKey(options)} onClick={() => { const key = nextOptionKey(options); if (key) setOptions([...options, { key, text: "" }]); }}>Add option</button><button type="button" className="secondary-button" disabled={options.length <= 2} onClick={() => { setCorrect(correct.filter((key) => key !== options[options.length - 1].key)); setOptions(options.slice(0, -1)); }}>Remove last option</button></div>}</fieldset>
    <label className="planner-wide">Explanation (optional)<textarea maxLength={5000} rows={3} value={explanation} onChange={(event) => setExplanation(event.target.value)} /></label>
    <Associations subject={subject} topic={topic} changeSubject={setSubject} changeTopic={setTopic} disabled={busy} /><SourceFields resource={resource} page={page} changeResource={setResource} changePage={setPage} disabled={busy} />
  </fieldset>{error && <p className="auth-error" role="alert">{error}</p>}<div className="planner-dialog-actions"><button className="primary-button" disabled={busy}>{busy ? "Saving…" : receipt ? "Confirm and save question" : "Save question"}</button></div></form></QuizDialog>;
}
