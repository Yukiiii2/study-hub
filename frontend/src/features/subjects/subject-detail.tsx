"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubject, getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { CurriculumError, CurriculumLoading } from "./load-state";
import { TopicHierarchy } from "./topic-hierarchy";
import { PageHeader } from "@/components/page-header";
import { SectionHeader } from "@/components/study-ui";
import { ProgressMeter } from "@/components/study-ui";
import { SubjectNavigation } from "./subject-navigation";
import { getSubjectVideos, type SubjectVideos } from "@/services/videos";
import { formatDuration } from "@/features/videos/duration";

export function SubjectDetail({ subjectId }: { subjectId: string }) {
  const [data, setData] = useState<{ subject: Subject; topics: Topic[] } | null>(null);
  const [error, setError] = useState<{ message: string; missing: boolean } | null>(null);
  const [retry, setRetry] = useState(0);
  const [lectures, setLectures] = useState<SubjectVideos | null>(null);
  const [lectureError, setLectureError] = useState(false);
  useEffect(() => {
    const controller = new AbortController(); setLectures(null); setLectureError(false);
    void getSubjectVideos(subjectId, controller.signal).then(value => { if (!controller.signal.aborted) setLectures(value); }).catch(() => { if (!controller.signal.aborted) setLectureError(true); });
    return () => controller.abort();
  }, [subjectId, retry]);
  const nextLecture = lectures?.videos.find(video => video.status === "in_progress") ?? lectures?.videos.find(video => video.status === "not_started");

  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError(null);
    void Promise.all([getSubject(subjectId, controller.signal), getSubjectTopics(subjectId, controller.signal)]).then(([subject, topics]) => {
      if (!controller.signal.aborted) setData({ subject, topics });
    }).catch((error: unknown) => {
      if (controller.signal.aborted) return;
      const missing = error instanceof ApiError && (error.status === 404 || error.status === 422);
      setError({ missing, message: missing ? "This subject is unavailable. Choose an active subject from the subject list." : error instanceof ApiError ? error.message : "Could not load this subject. Try again." });
    });
    return () => controller.abort();
  }, [subjectId, retry]);

  return <>
    <Link className="back-link" href="/subjects">All subjects</Link>
    {error ? error.missing ? <section className="curriculum-state"><h1>Subject not found</h1><p role="alert">{error.message}</p></section> :
      <CurriculumError message={error.message} retry={() => setRetry((value) => value + 1)} /> : data === null ? <CurriculumLoading /> : <>
      <div className="subject-overview subject-workspace-header" data-subject={data.subject.code}>
        <span className="subject-marker" data-color={data.subject.color_key ?? undefined} aria-hidden="true" />
        <PageHeader title={data.subject.name} description={`${data.subject.code} · ${data.topics.length} curriculum topics`} className="subject-heading" actions={<><Link className="primary-button" href={`/focus?subject_id=${encodeURIComponent(subjectId)}`}>Start Focus</Link><Link className="secondary-button" href={`/assistant?${new URLSearchParams({ subject_id: subjectId, mode: "ask" })}`}>Open Assistant</Link></>} />
      </div>
      <div className="subject-progress-rail" data-subject={data.subject.code}><div><span>Curriculum</span><strong>{data.topics.length} topics</strong></div><div>{lectures ? <ProgressMeter label="Lectures completed" value={lectures.summary.completed_videos} total={lectures.summary.total_videos} /> : <p>{lectureError ? "Lecture progress unavailable" : "Loading lecture progress…"}</p>}</div><div><span>Remaining lecture duration</span><strong>{lectures ? formatDuration(lectures.summary.remaining_duration_seconds) : "—"}</strong></div></div>
      {lectureError && <button className="ghost-button" onClick={() => setRetry(value => value + 1)}>Retry lecture progress</button>}
      {nextLecture && <section className="subject-continue" data-subject={data.subject.code}><div><span>Continue lecture</span><h2>{nextLecture.title}</h2><p>{nextLecture.topic_title} · {formatDuration(nextLecture.duration_seconds)}</p></div><Link className="secondary-button" href={`/subjects/${subjectId}/videos#video-${nextLecture.id}`}>Continue lecture</Link></section>}
      <SubjectNavigation subjectId={subjectId} current="curriculum" />
      <section className="subject-curriculum" aria-labelledby="topics-heading" data-subject={data.subject.code}>
        <SectionHeader title="Curriculum" titleId="topics-heading" detail={`${data.topics.length} ${data.topics.length === 1 ? "topic" : "topics"} · choose a topic to focus or prepare study material`} />
        {data.topics.length === 0 ? <div className="curriculum-state"><h3>Curriculum topics are not available yet</h3><p>Topics will appear here after curriculum import or setup. You can explore the other subjects in the meantime.</p></div> : <TopicHierarchy topics={data.topics} />}
      </section>
    </>}
  </>;
}
