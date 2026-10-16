import Link from "next/link";
import type { SubjectWorkspaceProps } from "./subject-desktop-workspace";
import { ProgressMeter, ContentSkeleton } from "@/components/study-ui";
import { SubjectNavigation } from "./subject-navigation";
import { TopicHierarchy } from "./topic-hierarchy";
import { formatDuration } from "@/features/videos/duration";

export function SubjectMobileWorkspace({ data, subjectId, lectures, nextLecture, lectureError, retry }: SubjectWorkspaceProps) {
  return <div className="mobile-subject-workspace" data-subject={data.subject.code}>
    <header className="mobile-subject-header"><span className="mobile-subject-code"><span className="subject-marker" aria-hidden="true" />{data.subject.code}</span><h1>{data.subject.name}</h1><div className="mobile-subject-actions"><Link className="primary-button" href={`/focus?subject_id=${subjectId}`}>Start Focus</Link><Link className="secondary-button" href={`/assistant?subject_id=${subjectId}&mode=ask`}>Assistant</Link></div></header>
    <section className="mobile-subject-progress" aria-label="Curriculum progress"><p>{data.topics.length} curriculum topics</p>{lectures ? <><ProgressMeter label="Lectures completed" value={lectures.summary.completed_videos} total={lectures.summary.total_videos} /><p className="resource-note">{formatDuration(lectures.summary.remaining_duration_seconds)} remaining lecture duration</p></> : lectureError ? <div className="resource-error"><p role="alert">Lecture progress unavailable.</p><button className="ghost-button" onClick={retry}>Retry progress</button></div> : <ContentSkeleton layout="control" label="Loading lecture progress…" />}</section>
    {nextLecture && <section className="mobile-subject-continue"><h2>Continue lecture</h2><p>{nextLecture.title}</p><span className="resource-note">{nextLecture.topic_title} · {formatDuration(nextLecture.duration_seconds)}</span><Link className="secondary-button" href={`/subjects/${subjectId}/videos#video-${nextLecture.id}`}>Continue lecture</Link></section>}
    <SubjectNavigation subjectId={subjectId} current="curriculum" />
    <section className="mobile-curriculum" aria-labelledby="topics-heading"><h2 id="topics-heading">Curriculum</h2>{data.topics.length ? <TopicHierarchy topics={data.topics} compact /> : <p className="mobile-empty">No curriculum topics available yet.</p>}</section>
  </div>;
}
