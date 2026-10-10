"use client";

import { useCallback, useState } from "react";
import { SectionHeader, StatusBadge } from "@/components/study-ui";
import { createAssessment, updateAssessment, assessmentError, type Assessment, type AssessmentInput, type AssessmentStatus } from "@/services/assessments";
import { getSubjects, getSubjectTopics } from "@/services/subjects";
import { LoadNotice, QuizDialog, useQuizLoad } from "@/features/quizzes/shared";
import { assessmentEditedInstant, assessmentLocal, wholeSubjectCoverage } from "./form-state";
import { assessmentLoad } from "./load";

export function AssessmentEditor({ assessment, timezone, close, saved }: { assessment?: Assessment; timezone: string; close: () => void; saved: (assessment: Assessment) => void }) {
  const [title, setTitle] = useState(assessment?.title ?? "");
  const [description, setDescription] = useState(assessment?.description ?? "");
  const [scheduled, setScheduled] = useState(() => assessmentLocal(assessment?.scheduled_at, timezone));
  const [status, setStatus] = useState<AssessmentStatus>(assessment?.status ?? "planned");
  const [subjectIds, setSubjectIds] = useState(assessment?.subject_ids ?? []);
  const [topicIds, setTopicIds] = useState(assessment?.topic_ids ?? []);
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null);
  const curriculum = useQuizLoad(useCallback((signal) => assessmentLoad((async () => { const subjects = await getSubjects(signal); const topics = (await Promise.all(subjects.map((subject) => getSubjectTopics(subject.id, signal)))).flat(); return { subjects, topics }; })()), []));
  async function save() {
    if (!title.trim()) { setError("Enter an assessment title."); return; }
    if (!curriculum.data || curriculum.loading || curriculum.error) { setError("Load the coverage options before saving."); return; }
    setBusy(true); setError(null);
    try {
      const body: AssessmentInput = { title: title.trim(), description: description.trim() || null, scheduled_at: assessmentEditedInstant(scheduled, timezone, assessment?.scheduled_at), status, subject_ids: subjectIds, topic_ids: topicIds };
      const result = assessment ? await updateAssessment(assessment.id, body) : await createAssessment(body); saved(result); close();
    } catch (failure) { setError(assessmentError(failure)); } finally { setBusy(false); }
  }
  function setWholeSubject(id: string, all: boolean) {
    setSubjectIds((current) => all ? [...current.filter((value) => value !== id), id] : current.filter((value) => value !== id));
    if (all && curriculum.data) setTopicIds((current) => wholeSubjectCoverage(current, id, curriculum.data!.topics));
  }
  return <QuizDialog title={assessment ? "Edit assessment" : "New assessment"} busy={busy} close={close}><form className="assessment-definition-form" onSubmit={(event) => { event.preventDefault(); void save(); }}><fieldset disabled={busy} className="planner-form-grid"><label className="planner-wide">Title<input autoFocus required maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} /></label><label className="planner-wide">Description (optional)<textarea rows={3} maxLength={5000} value={description} onChange={(event) => setDescription(event.target.value)} /></label><label>Assessment date and time (optional)<input type="datetime-local" value={scheduled} onChange={(event) => setScheduled(event.target.value)} /></label><label>Status<select value={status} onChange={(event) => setStatus(event.target.value as AssessmentStatus)}><option value="planned">Planned</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select></label><p className="planner-wide resource-note">Dates use {timezone}. You can leave the date and coverage unset until known. Definition status and result history are recorded separately.</p><div className="planner-wide assessment-coverage-editor"><SectionHeader title="Coverage" detail="Choose all topics in a subject or select individual topics. Whole-subject coverage includes future topics added to that subject." /><LoadNotice loading={curriculum.loading} error={curriculum.error} retry={curriculum.retry} />{curriculum.data && !curriculum.error && curriculum.data.subjects.map((subject) => {
    const all = subjectIds.includes(subject.id), topics = curriculum.data!.topics.filter((topic) => topic.subject_id === subject.id), selected = topics.filter((topic) => topicIds.includes(topic.id)).length;
    return <details className="assessment-subject-options" key={subject.id}><summary>{subject.code} — {subject.name}<StatusBadge tone={all || selected ? "info" : "neutral"}>{all ? "All topics" : `${selected} selected`}</StatusBadge></summary><fieldset disabled={busy}><legend className="quiz-sr-only">Coverage for {subject.code}</legend><div className="assessment-scope-options"><label className="planner-check"><input type="radio" name={`scope-${subject.id}`} checked={all} onChange={() => setWholeSubject(subject.id, true)} />All topics</label><label className="planner-check"><input type="radio" name={`scope-${subject.id}`} checked={!all} onChange={() => setWholeSubject(subject.id, false)} />Select topics</label></div>{!all && <div className="assessment-topic-options">{!topics.length && <p className="resource-note">No active topics in this subject.</p>}{topics.map((topic) => <label className="planner-check" key={topic.id}><input type="checkbox" checked={topicIds.includes(topic.id)} onChange={(event) => setTopicIds((current) => event.target.checked ? [...current.filter((id) => id !== topic.id), topic.id] : current.filter((id) => id !== topic.id))} />{topic.code ? `${topic.code} — ` : ""}{topic.title}</label>)}</div>}</fieldset></details>;
  })}</div></fieldset>{error && <p role="alert" className="auth-error">{error}</p>}<div className="planner-dialog-actions"><button type="button" className="secondary-button" disabled={busy} onClick={close}>Cancel</button><button className="primary-button" disabled={busy || curriculum.loading || !!curriculum.error || !curriculum.data}>{busy ? "Saving…" : "Save assessment"}</button></div></form></QuizDialog>;
}
