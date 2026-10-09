"use client";

import { useState } from "react";
import { commitQuestions, previewQuestions, questionCsvError, quizError, type ImportPreview } from "@/services/quizzes";
import { QuizDialog } from "./shared";

export function QuestionImport({ close, saved }: { close: () => void; saved: (message: string) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function inspect() {
    if (!file) { setError("Choose a CSV file."); return; }
    const failure = questionCsvError(file); if (failure) { setError(failure); return; }
    setBusy(true); setError(null); setPreview(null);
    try { setPreview(await previewQuestions(file)); } catch (failure) { setError(quizError(failure)); } finally { setBusy(false); }
  }
  async function commit() {
    if (!file || !preview?.preview_token || preview.errors.length) return;
    setBusy(true); setError(null);
    try { const result = await commitQuestions(file, preview.preview_token); saved(`Imported ${result.inserted} questions. ${result.unchanged} unchanged.`); close(); }
    catch (failure) { setError(quizError(failure)); } finally { setBusy(false); }
  }
  return <QuizDialog title="Import question CSV" close={close} busy={busy}><p className="resource-note">UTF-8 CSV, up to 1 MiB and 500 rows. Preview validates the file before confirmation. No questions are saved by preview.</p><details className="quiz-csv-help"><summary>CSV format</summary><p>Required headers: question, correct_answer. Optional: subject, topic, question_type, option_a through option_f, explanation, resource_id, source_page.</p><p>Types: single_select (default), multi_select, true_false. Multi-select answers use semicolons, such as A;C. True/false answers use TRUE or FALSE with blank option columns. Subject and topic codes must match existing entries.</p></details>
    <form onSubmit={(event) => { event.preventDefault(); void inspect(); }}><label className="quiz-file">CSV file<input autoFocus type="file" required accept=".csv,text/csv" disabled={busy} onChange={(event) => { const next = event.target.files?.[0] ?? null; setFile(next); setPreview(null); setError(next ? questionCsvError(next) : null); }} /></label><div className="planner-dialog-actions"><button className="secondary-button" disabled={busy}>{busy ? "Working…" : "Preview CSV"}</button></div></form>
    {error && <p role="alert" className="auth-error">{error}</p>}{preview && <section className="quiz-import-preview" aria-label="CSV preview"><h3>Preview</h3><p>{preview.row_count} rows · {preview.valid_count} valid · {preview.proposed_inserts} to insert · {preview.unchanged} unchanged · {preview.duplicate_count} duplicates · {preview.warnings.length} warnings · {preview.errors.length} errors</p>{preview.errors.length > 0 && <p role="alert" className="auth-error">Errors block all imports. Correct the file and preview it again.</p>}{[...preview.errors, ...preview.warnings].map((issue, index) => <p className="resource-note" key={index}>Row {issue.row}, {issue.field}: {issue.message}</p>)}{preview.sample.length > 0 && <><h4>Sample questions</h4><ol className="quiz-import-samples">{preview.sample.map((question, index) => <li key={index}><p>{question.prompt}</p><ul>{question.options.map((option) => <li key={option.key}>{option.key}: {option.text}</li>)}</ul><p className="resource-note">Correct: {question.correct_keys.join(", ")}</p></li>)}</ol></>}<div className="planner-dialog-actions"><button type="button" className="primary-button" disabled={busy || !!preview.errors.length || !preview.preview_token} onClick={() => void commit()}>Confirm import</button></div></section>}
  </QuizDialog>;
}
