"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubject, getSubjectTopics, type Subject, type Topic } from "@/services/subjects";
import { CurriculumError, CurriculumLoading } from "./load-state";
import { TopicHierarchy } from "./topic-hierarchy";

export function SubjectDetail({ subjectId }: { subjectId: string }) {
  const [data, setData] = useState<{ subject: Subject; topics: Topic[] } | null>(null);
  const [error, setError] = useState<{ message: string; missing: boolean } | null>(null);
  const [retry, setRetry] = useState(0);

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
      <header className="page-heading subject-heading">
        <span className="subject-marker" data-color={data.subject.color_key ?? undefined} aria-hidden="true" />
        <div><h1>{data.subject.code}</h1><p>{data.subject.name}</p></div>
      </header>
      <section aria-labelledby="topics-heading">
        <div className="section-heading"><h2 id="topics-heading">Topics</h2><span>{data.topics.length} {data.topics.length === 1 ? "topic" : "topics"}</span></div>
        {data.topics.length === 0 ? <div className="curriculum-state"><h3>Curriculum topics are not available yet</h3><p>Topics will appear here after curriculum import or setup. You can explore the other subjects in the meantime.</p></div> : <TopicHierarchy topics={data.topics} />}
      </section>
    </>}
  </>;
}
