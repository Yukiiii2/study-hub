"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubjects, type Subject } from "@/services/subjects";
import { CurriculumError, CurriculumLoading } from "./load-state";
import { PageHeader } from "@/components/page-header";
import { SectionHeader } from "@/components/study-ui";
import { InterfaceIcon } from "@/components/interface-icon";
import { getDashboard, type DashboardData } from "@/services/dashboard";
import { LoadingNotice, ProgressMeter } from "@/components/study-ui";

export function SubjectsList() {
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const [progress, setProgress] = useState<DashboardData["subjects"] | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    void getDashboard(controller.signal).then(data => { if (!controller.signal.aborted) setProgress(data.subjects); }).catch(() => {});
    return () => controller.abort();
  }, [retry]);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    void getSubjects(controller.signal).then((data) => {
      if (!controller.signal.aborted) setSubjects(data);
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setError(error instanceof ApiError ? error.message : "Could not load subjects. Try again.");
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [retry]);

  return <>
    <PageHeader title="Subjects" description="Your CPALE curriculum, organized by subject." />
    {error && <CurriculumError message={error} retry={() => setRetry((value) => value + 1)} />}{loading && subjects && <LoadingNotice>Refreshing subjects…</LoadingNotice>}{subjects === null ? !error && <CurriculumLoading /> : subjects.length === 0 ?
      <section className="curriculum-state"><h2>No subjects available</h2><p>Active subjects will appear here once curriculum setup is complete.</p></section> :
      <section aria-labelledby="subject-directory-heading"><SectionHeader title="Your curriculum" titleId="subject-directory-heading" detail={`${subjects.length} ${subjects.length === 1 ? "subject" : "subjects"}`} />
      <ul className="subject-list" aria-label="Subjects">{subjects.map((subject) => <li key={subject.id} data-subject={subject.code}>
        <Link href={`/subjects/${subject.id}`} className="subject-row">
          <span className="subject-marker" data-color={subject.color_key ?? undefined} aria-hidden="true" />
          <span className="subject-code">{subject.code}</span>
          <span className="subject-name">{subject.name}</span>
          <div className="subject-list-progress">{progress?.find(item => item.id === subject.id) ? <><ProgressMeter label="Lectures completed" value={progress.find(item => item.id === subject.id)!.completed_video_count} total={progress.find(item => item.id === subject.id)!.video_count} /><span>{progress.find(item => item.id === subject.id)!.topic_count} topics</span></> : <span>Open curriculum and lecture progress</span>}</div>
          <span className="subject-open"><InterfaceIcon name="next" /></span>
        </Link>
      </li>)}</ul></section>}
  </>;
}
