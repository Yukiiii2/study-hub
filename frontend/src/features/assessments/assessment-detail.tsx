"use client";

import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { SectionHeader, StatusBadge } from "@/components/study-ui";
import { useCallback, useState } from "react";
import { archiveAssessment, assessmentError, getAssessment, getAssessmentAttempts, type AssessmentAttempt } from "@/services/assessments";
import { LoadNotice, Pagination, QuizDialog, useQuizLoad } from "@/features/quizzes/shared";
import { AssessmentEditor } from "./assessment-editor";
import { AttemptEditor } from "./attempt-editor";
import { AttemptHistoryView, CoverageView, ReadinessView } from "./assessment-views";
import { assessmentTimestamp } from "./form-state";
import { assessmentLoad } from "./load";

export function AssessmentDetailPage({ id }: { id: string }) {
  const [offset, setOffset] = useState(0);
  const assessment = useQuizLoad(useCallback((signal) => assessmentLoad(getAssessment(id, signal)), [id]));
  const history = useQuizLoad(useCallback((signal) => assessmentLoad(getAssessmentAttempts(id, { offset, limit: 20 }, signal).then((data) => ({ ...data, offset }))), [id, offset]));
  const [editing, setEditing] = useState(false), [result, setResult] = useState<AssessmentAttempt | "new" | null>(null), [archiving, setArchiving] = useState(false);
  const [busy, setBusy] = useState(false), [error, setError] = useState<string | null>(null), [notice, setNotice] = useState<string | null>(null);
  const data = assessment.data, archived = data?.status === "archived", timezone = data?.readiness.timezone;
  const refresh = () => { assessment.retry(); history.retry(); };
  async function archive() {
    setBusy(true); setError(null);
    try { await archiveAssessment(id); setArchiving(false); setNotice("Assessment archived. Coverage and result history have been retained."); refresh(); }
    catch (failure) { setError(assessmentError(failure)); } finally { setBusy(false); }
  }
  return <><Link className="resource-back" href="/assessments">Back to assessments</Link><LoadNotice loading={assessment.loading} error={assessment.error} retry={assessment.retry} />{notice && <p className="resource-note" role="status">{notice}</p>}{data && !assessment.loading && !assessment.error && timezone && <><PageHeader title={data.title} description="Track coverage, study activity and recorded results." meta={<><span>{data.scheduled_at ? <time dateTime={data.scheduled_at}>{assessmentTimestamp(data.scheduled_at, timezone)}</time> : "Date not set"} · {timezone}</span><StatusBadge tone={data.status === "completed" ? "success" : data.status === "planned" ? "info" : "neutral"}>{data.status}</StatusBadge></>} actions={!archived && <><button type="button" className="secondary-button" onClick={() => setEditing(true)}>Edit assessment</button><button type="button" className="ghost-button" onClick={() => { setError(null); setArchiving(true); }}>Archive</button><button type="button" className="primary-button" onClick={() => setResult("new")}>Record result</button></>} />{data.description && <p className="assessment-description">{data.description}</p>}{archived && <p className="resource-note">This assessment is archived. Its coverage and result history remain available; results cannot be added or edited.</p>}<div className="assessment-overview"><CoverageView assessment={data} /><ReadinessView readiness={data.readiness} /></div><section className="assessment-section" aria-labelledby="assessment-results"><SectionHeader titleId="assessment-results" title="Result history" detail="Manual attempts are separate from the assessment definition. Unscored attempts remain unscored." /><LoadNotice loading={history.loading} error={history.error} retry={history.retry} />{!history.loading && !history.error && history.data?.offset === offset && <><AttemptHistoryView attempts={history.data.attempts} timezone={timezone} archived={!!archived} edit={setResult} /><Pagination offset={offset} total={history.data.total} change={setOffset} busy={history.loading} /></>}</section>{editing && !archived && <AssessmentEditor assessment={data} timezone={timezone} close={() => setEditing(false)} saved={() => { setNotice("Assessment saved."); refresh(); }} />}{result && !archived && <AttemptEditor assessmentId={id} attempt={result === "new" ? undefined : result} timezone={timezone} close={() => setResult(null)} saved={() => { setOffset(0); setNotice("Result saved."); refresh(); }} />}{archiving && !archived && <QuizDialog title="Archive assessment" close={() => setArchiving(false)} busy={busy}><p>Archive “{data.title}”? Its coverage and result history will be retained. New results and corrections will be unavailable while archived.</p>{error && <p className="auth-error" role="alert">{error}</p>}<div className="planner-dialog-actions"><button type="button" className="secondary-button" disabled={busy} onClick={() => setArchiving(false)}>Keep assessment</button><button type="button" className="danger-button" disabled={busy} onClick={() => void archive()}>{busy ? "Archiving…" : "Archive assessment"}</button></div></QuizDialog>}</>}</>;
}
