"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubject, getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { getSubjectVideos, setVideoProgress, type SubjectVideos, type VideoStatus } from "@/services/videos";
import { CurriculumLoading, CurriculumError } from "@/features/subjects/load-state";
import { flattenTopics } from "@/features/subjects/hierarchy";
import { formatDuration } from "./duration";
import { PageHeader } from "@/components/page-header";
import { LoadingNotice, ProgressMeter, SectionHeader, StatusBadge } from "@/components/study-ui";
import { SubjectNavigation } from "@/features/subjects/subject-navigation";

type PageData = { subject: Subject; topics: Topic[]; lectures: SubjectVideos };

export function SubjectVideosPage({ subjectId }: { subjectId: string }) {
  const [savedData, setData] = useState<PageData | null>(null);
  const data = savedData?.subject.id === subjectId ? savedData : null;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; missing: boolean } | null>(null);
  const [retry, setRetry] = useState(0);
  const [pending, setPending] = useState<string | null>(null);
  const [updateError, setUpdateError] = useState<{ id: string; message: string } | null>(null);
  const [notice, setNotice] = useState("");
  const saving = useRef(false);
  const lifetime = useRef<AbortController | null>(null);
  useEffect(() => {
    if (!data || !window.location.hash.startsWith("#video-")) return;
    document.getElementById(window.location.hash.slice(1))?.scrollIntoView({ block: "center" });
  }, [data?.subject.id]);

  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    setLoading(true); setError(null); setUpdateError(null); setNotice(""); setPending(null);
    saving.current = false;
    void Promise.all([getSubject(subjectId, controller.signal), getSubjectTopics(subjectId, controller.signal), getSubjectVideos(subjectId, controller.signal)])
      .then(([subject, topics, lectures]) => { if (!controller.signal.aborted) setData({ subject, topics, lectures }); })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const missing = error instanceof ApiError && (error.status === 404 || error.status === 422);
        setError({ missing, message: missing ? "This subject is unavailable. Choose another subject." : error instanceof ApiError ? error.message : "Could not load videos. Try again." });
      }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [subjectId, retry]);

  async function changeStatus(id: string, status: VideoStatus) {
    if (saving.current || !lifetime.current) return;
    const controller = lifetime.current;
    saving.current = true; setPending(id); setUpdateError(null); setNotice("");
    let saved = false;
    try {
      await setVideoProgress(id, status, controller.signal);
      saved = true;
      const lectures = await getSubjectVideos(subjectId, controller.signal);
      if (!controller.signal.aborted) {
        setData((current) => current ? { ...current, lectures } : current);
        setNotice("Video status saved.");
      }
    } catch (error: unknown) {
      if (!controller.signal.aborted) setUpdateError({ id, message: saved ? "Status saved, but the list could not refresh. Retry loading to see the saved status." : error instanceof ApiError ? error.message : "Video status could not be saved. Try again." });
    } finally {
      if (!controller.signal.aborted) { saving.current = false; setPending(null); }
    }
  }

  const grouped = new Map<string, SubjectVideos["videos"]>();
  for (const video of data?.lectures.videos ?? []) {
    const group = grouped.get(video.topic_id) ?? [];
    group.push(video); grouped.set(video.topic_id, group);
  }

  return <>
    <Link className="back-link" href={`/subjects/${subjectId}`}>Subject topics</Link>
    {error && (error.missing ? <section className="curriculum-state"><h1>Subject not found</h1><p role="alert">{error.message}</p><Link className="back-link" href="/subjects">All subjects</Link></section> :
      <CurriculumError message={error.message} retry={() => setRetry((value) => value + 1)} />)}
    {loading && data && <LoadingNotice>Refreshing lectures…</LoadingNotice>}
    {error?.missing ? null : data === null ? !error && <CurriculumLoading /> : <>
      <div className="subject-overview subject-workspace-header" data-subject={data.subject.code}>
        <span className="subject-marker" data-color={data.subject.color_key ?? undefined} aria-hidden="true" />
        <PageHeader title={`${data.subject.code} lectures`} description={data.subject.name} className="subject-heading" actions={<Link className="primary-button" href={`/focus?subject_id=${subjectId}`}>Start Focus</Link>} />
      </div>
      <SubjectNavigation subjectId={subjectId} current="lectures" />
      <section className="lecture-progress" aria-labelledby="lecture-progress-heading">
      <SectionHeader title="Lecture progress" titleId="lecture-progress-heading" />
      <ProgressMeter value={data.lectures.summary.completed_videos} total={data.lectures.summary.total_videos} label="Videos completed" />
      <dl className="video-summary" aria-label="Your lecture progress">
        <div><dt>Completed lecture time</dt><dd>{formatDuration(data.lectures.summary.completed_duration_seconds)}</dd></div>
        <div><dt>Remaining lecture time</dt><dd>{formatDuration(data.lectures.summary.remaining_duration_seconds)}</dd></div>
      </dl>
      <p className="video-summary-note">Time is the duration of lectures marked complete, rather than measured study time. Durations use h:mm:ss or m:ss.</p>
      {data.lectures.summary.unknown_duration_videos > 0 && <p className="video-summary-note">{data.lectures.summary.unknown_duration_videos} videos have no duration and are excluded from time totals.</p>}
      </section>
      <p className="sr-only" role="status" aria-live="polite">{pending ? "Saving video status..." : notice}</p>
      {updateError && <div className="video-update-error"><p id="video-update-message" role="alert" className="auth-error">{updateError.message}</p><button className="secondary-button" disabled={pending !== null} onClick={() => setRetry((value) => value + 1)}>Reload videos</button></div>}
      {data.lectures.videos.length === 0 ? <section className="curriculum-state"><h2>No videos available</h2><p>No lectures are available for this subject yet. Its curriculum topics remain available.</p></section> :
        flattenTopics(data.topics).map(({ topic }) => {
          const videos = grouped.get(topic.id) ?? [];
          return <section key={topic.id} className="video-topic" aria-labelledby={`video-topic-${topic.id}`}>
            <div className="video-topic-heading">{topic.code && <span className="topic-code">{topic.code}</span>}<SectionHeader title={topic.title} titleId={`video-topic-${topic.id}`} detail={`${videos.filter((video) => video.status === "completed").length} / ${videos.length} videos completed`} /></div>
            {videos.length === 0 ? <p className="video-empty-topic">No lectures are available for this topic.</p> : <ul className="video-list">
              {videos.map((video) => <li key={video.id} id={`video-${video.id}`} className="video-row" data-status={video.status}>
                <div className="video-copy"><div className="video-title"><h3>{video.title}</h3></div><div className="video-row-meta"><span className="video-duration">{formatDuration(video.duration_seconds)}</span><StatusBadge tone={video.status === "completed" ? "success" : video.status === "in_progress" ? "info" : "neutral"}>{video.status === "completed" ? "Completed" : video.status === "in_progress" ? "In progress" : "Not started"}</StatusBadge></div></div>
                <label className="video-progress-control"><span className="sr-only">Status for {video.title}</span>
                  <select value={video.status} disabled={pending !== null} aria-busy={pending === video.id} aria-describedby={updateError?.id === video.id ? "video-update-message" : undefined} onChange={(event) => void changeStatus(video.id, event.target.value as VideoStatus)}>
                    <option value="not_started">Not started</option><option value="in_progress">In progress</option><option value="completed">Completed</option>
                  </select>
                  {pending === video.id && <span className="video-saving">Saving...</span>}
                </label>
              </li>)}
            </ul>}
          </section>;
        })}
    </>}
  </>;
}
