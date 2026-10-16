"use client";

import { ResponsiveView } from "@/components/responsive-view";
import { SubjectsDesktopView } from "./subjects-desktop-view";
import { SubjectsMobileView } from "./subjects-mobile-view";
import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubjects, type Subject } from "@/services/subjects";
import { CurriculumError, CurriculumLoading } from "./load-state";
import { PageHeader } from "@/components/page-header";
import { SectionHeader } from "@/components/study-ui";
import { getDashboard, type DashboardData } from "@/services/dashboard";
import { LoadingNotice } from "@/components/study-ui";

export function SubjectsList() {
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);
  const [progress, setProgress] = useState<DashboardData["subjects"] | null>(null);
  const [loading, setLoading] = useState(true);
  const [progressError, setProgressError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    setProgressError(false);
    void getDashboard(controller.signal).then(data => { if (!controller.signal.aborted) setProgress(data.subjects); }).catch(() => { if (!controller.signal.aborted) setProgressError(true); });
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
      {progressError && <div className="resource-error"><p role="alert">Lecture progress could not refresh. Curriculum remains available.</p><button className="ghost-button" onClick={() => setRetry(value => value + 1)}>Retry progress</button></div>}<ResponsiveView desktop={() => <SubjectsDesktopView subjects={subjects} progress={progress} />} mobile={() => <SubjectsMobileView subjects={subjects} progress={progress} />} /></section>}
  </>;
}
