"use client";

import Link from "next/link";
import { ResponsiveView } from "@/components/responsive-view";
import { SubjectDesktopWorkspace } from "./subject-desktop-workspace";
import { SubjectMobileWorkspace } from "./subject-mobile-workspace";
import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubject, getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { CurriculumError, CurriculumLoading } from "./load-state";
import { LoadingNotice } from "@/components/study-ui";
import { getSubjectVideos, type SubjectVideos } from "@/services/videos";

export function SubjectDetail({ subjectId }: { subjectId: string }) {
  const [savedData, setData] = useState<{ subject: Subject; topics: Topic[] } | null>(null);
  const data = savedData?.subject.id === subjectId ? savedData : null;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<{ message: string; missing: boolean } | null>(null);
  const [retry, setRetry] = useState(0);
  const [lectureSnapshot, setLectures] = useState<{ subjectId: string; data: SubjectVideos } | null>(null);
  const lectures = lectureSnapshot?.subjectId === subjectId ? lectureSnapshot.data : null;
  const [lectureError, setLectureError] = useState(false);
  useEffect(() => {
    const controller = new AbortController(); setLectureError(false);
    void getSubjectVideos(subjectId, controller.signal).then(value => { if (!controller.signal.aborted) setLectures({ subjectId, data: value }); }).catch(() => { if (!controller.signal.aborted) setLectureError(true); });
    return () => controller.abort();
  }, [subjectId, retry]);
  const nextLecture = lectures?.videos.find(video => video.status === "in_progress") ?? lectures?.videos.find(video => video.status === "not_started");

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    void Promise.all([getSubject(subjectId, controller.signal), getSubjectTopics(subjectId, controller.signal)]).then(([subject, topics]) => {
      if (!controller.signal.aborted) setData({ subject, topics });
    }).catch((error: unknown) => {
      if (controller.signal.aborted) return;
      const missing = error instanceof ApiError && (error.status === 404 || error.status === 422);
      setError({ missing, message: missing ? "This subject is unavailable. Choose an active subject from the subject list." : error instanceof ApiError ? error.message : "Could not load this subject. Try again." });
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [subjectId, retry]);

  return <>
    <Link className="back-link" href="/subjects">All subjects</Link>
    {error && (error.missing ? <section className="curriculum-state"><h1>Subject not found</h1><p role="alert">{error.message}</p></section> :
      <CurriculumError message={error.message} retry={() => setRetry((value) => value + 1)} />)}
    {loading && data && <LoadingNotice>Refreshing curriculum…</LoadingNotice>}
    {error?.missing ? null : data === null ? !error && <CurriculumLoading layout="detail" /> : <>
      <ResponsiveView desktop={() => <SubjectDesktopWorkspace data={data} subjectId={subjectId} lectures={lectures} nextLecture={nextLecture} lectureError={lectureError} retry={() => setRetry(value => value + 1)} />} mobile={() => <SubjectMobileWorkspace data={data} subjectId={subjectId} lectures={lectures} nextLecture={nextLecture} lectureError={lectureError} retry={() => setRetry(value => value + 1)} />} />
    </>}
  </>;
}
