"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getSubjects, type Subject } from "@/services/subjects";
import { CurriculumError, CurriculumLoading } from "./load-state";

export function SubjectsList() {
  const [subjects, setSubjects] = useState<Subject[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setSubjects(null);
    setError(null);
    void getSubjects(controller.signal).then((data) => {
      if (!controller.signal.aborted) setSubjects(data);
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setError(error instanceof ApiError ? error.message : "Could not load subjects. Try again.");
    });
    return () => controller.abort();
  }, [retry]);

  return <>
    <header className="page-heading"><h1>Subjects</h1><p>Your CPALE curriculum, organized by subject.</p></header>
    {error ? <CurriculumError message={error} retry={() => setRetry((value) => value + 1)} /> : subjects === null ? <CurriculumLoading /> : subjects.length === 0 ?
      <section className="curriculum-state"><h2>No subjects available</h2><p>Active subjects will appear here once curriculum setup is complete.</p></section> :
      <ul className="subject-list" aria-label="Subjects">{subjects.map((subject) => <li key={subject.id}>
        <Link href={`/subjects/${subject.id}`} className="subject-row">
          <span className="subject-marker" data-color={subject.color_key ?? undefined} aria-hidden="true" />
          <span className="subject-code">{subject.code}</span>
          <span className="subject-name">{subject.name}</span>
          <span className="subject-open" aria-hidden="true">›</span>
        </Link>
      </li>)}</ul>}
  </>;
}
