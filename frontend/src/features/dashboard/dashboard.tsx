"use client";

import { useState } from "react";
import { ApiError, authenticatedGet } from "@/services/api";
import { DashboardPlaceholder } from "./dashboard-placeholder";

export function Dashboard() {
  const [subjectCount, setSubjectCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checking, setChecking] = useState(false);

  async function checkSubjects() {
    setChecking(true); setError(null); setSubjectCount(null);
    try {
      const subjects = await authenticatedGet<{ id: string; code: string }[]>("/api/subjects");
      setSubjectCount(subjects.length);
    } catch (error) {
      setError(error instanceof ApiError ? error.message : "Could not check subject setup. Try again.");
    } finally { setChecking(false); }
  }

  return <><DashboardPlaceholder />
    <section className="integration-check" aria-label="Subject setup check">
      <button className="secondary-button" onClick={checkSubjects} disabled={checking}>
        {checking ? "Checking subject setup..." : "Check subject setup"}
      </button>
      {subjectCount !== null && <p role="status">{subjectCount} subject definitions available.</p>}
      {error && <p className="auth-error" role="alert">{error}</p>}
    </section>
  </>;
}
