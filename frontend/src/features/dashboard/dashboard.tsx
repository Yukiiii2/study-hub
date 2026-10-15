"use client";

import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getDashboard, type DashboardData } from "@/services/dashboard";
import { getFocus, getAnalytics } from "@/services/analytics";
import { getAssessments } from "@/services/assessments";
import { elapsedSeconds, type ClockAnchor } from "@/features/analytics/presentation";
import type { DashboardExtras } from "./dashboard-view";
import { DashboardView } from "./dashboard-view";

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(true);
  const [revision, setRevision] = useState(0);
  const [extras, setExtras] = useState<DashboardExtras>({ focus: null, activity: null, assessments: null });
  const [anchor, setAnchor] = useState<ClockAnchor | null>(null);
  const [extraErrors, setExtraErrors] = useState<string[]>([]);
  const [extrasLoading, setExtrasLoading] = useState(true);
  const [, setTick] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setRefreshing(true); setError(null);
    void getDashboard(controller.signal).then((result) => {
      if (!controller.signal.aborted) setData(result);
    }).catch((error: unknown) => {
      if (!controller.signal.aborted) setError(error instanceof ApiError ? error.message : "Could not load your dashboard. Try again.");
    }).finally(() => { if (!controller.signal.aborted) setRefreshing(false); });
    return () => controller.abort();
  }, [revision]);

  // Refresh each supplemental panel without clearing the existing workspace.
  useEffect(() => {
    if (!data) return;
    const controller = new AbortController();
    setExtrasLoading(true);
    void Promise.allSettled([
      getFocus(controller.signal), getAnalytics({ period: 7 }, controller.signal),
      getAssessments({ status: "planned", limit: 20 }, controller.signal),
    ]).then(([focus, activity, assessments]) => {
      if (controller.signal.aborted) return;
      setExtras((previous) => ({
        focus: focus.status === "fulfilled" ? focus.value : previous.focus,
        activity: activity.status === "fulfilled" ? activity.value : previous.activity,
        assessments: assessments.status === "fulfilled" ? assessments.value.assessments : previous.assessments,
      }));
      if (focus.status === "fulfilled") setAnchor({ serverTime: Date.parse(focus.value.server_now), monotonicTime: performance.now() });
      setExtraErrors([focus.status === "rejected" ? "Focus" : "", activity.status === "rejected" ? "Weekly activity" : "", assessments.status === "rejected" ? "Assessments" : ""].filter(Boolean));
      setExtrasLoading(false);
    });
    return () => controller.abort();
  }, [data]);

  useEffect(() => {
    if (!extras.focus?.active_session) return;
    const timer = window.setInterval(() => setTick((value) => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [extras.focus?.active_session?.id]);

  const elapsed = extras.focus?.active_session && anchor ? elapsedSeconds(extras.focus.active_session.started_at, anchor, performance.now()) : 0;
  return <DashboardView data={data} extras={extras} extrasLoading={extrasLoading} elapsed={elapsed} extraErrors={extraErrors} error={error} refreshing={refreshing} onRefresh={() => setRevision((value) => value + 1)} />;
}
