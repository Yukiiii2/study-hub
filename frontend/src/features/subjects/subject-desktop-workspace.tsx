import Link from "next/link";
import type { Subject, Topic } from "@/services/subjects";
import type { SubjectVideos, Video } from "@/services/videos";
import { PageHeader } from "@/components/page-header";
import { SectionHeader, ContentSkeleton, ProgressMeter } from "@/components/study-ui";
import { SubjectNavigation } from "./subject-navigation";
import { TopicHierarchy } from "./topic-hierarchy";
import { formatDuration } from "@/features/videos/duration";
export type SubjectWorkspaceProps = { data: { subject: Subject; topics: Topic[] }; subjectId: string; lectures: SubjectVideos | null; nextLecture?: Video; lectureError: boolean; retry: () => void };
export function SubjectDesktopWorkspace({ data, subjectId, lectures, nextLecture, lectureError, retry }: SubjectWorkspaceProps) { return <><div className="subject-overview subject-workspace-header" data-subject={data.subject.code}>
        <span className="subject-marker" data-color={data.subject.color_key ?? undefined} aria-hidden="true" />
        <PageHeader title={data.subject.name} description={`${data.subject.code} · ${data.topics.length} curriculum topics`} className="subject-heading" actions={<><Link className="primary-button" href={`/focus?subject_id=${encodeURIComponent(subjectId)}`}>Start Focus</Link><Link className="secondary-button" href={`/assistant?${new URLSearchParams({ subject_id: subjectId, mode: "ask" })}`}>Open Assistant</Link></>} />
      </div>
      <div className="subject-progress-rail" data-subject={data.subject.code}><div><span>Curriculum</span><strong>{data.topics.length} topics</strong></div><div>{lectures ? <ProgressMeter label="Lectures completed" value={lectures.summary.completed_videos} total={lectures.summary.total_videos} /> : lectureError ? <p>Lecture progress unavailable</p> : <ContentSkeleton layout="control" label="Loading lecture progress…" />}</div><div><span>Remaining lecture duration</span><strong>{lectures ? formatDuration(lectures.summary.remaining_duration_seconds) : "—"}</strong></div></div>
      {lectureError && <button className="ghost-button" onClick={() => retry()}>Retry lecture progress</button>}
      {nextLecture && <section className="subject-continue" data-subject={data.subject.code}><div><span>Continue lecture</span><h2>{nextLecture.title}</h2><p>{nextLecture.topic_title} · {formatDuration(nextLecture.duration_seconds)}</p></div><Link className="secondary-button" href={`/subjects/${subjectId}/videos#video-${nextLecture.id}`}>Continue lecture</Link></section>}
      <SubjectNavigation subjectId={subjectId} current="curriculum" />
      <section className="subject-curriculum" aria-labelledby="topics-heading" data-subject={data.subject.code}>
        <SectionHeader title="Curriculum" titleId="topics-heading" detail={`${data.topics.length} ${data.topics.length === 1 ? "topic" : "topics"} · choose a topic to focus or prepare study material`} />
        {data.topics.length === 0 ? <div className="curriculum-state"><h3>Curriculum topics are not available yet</h3><p>Topics will appear here after curriculum import or setup. You can explore the other subjects in the meantime.</p></div> : <TopicHierarchy topics={data.topics} />}
      </section></>; }
