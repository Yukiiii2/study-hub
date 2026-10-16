"use client";
import { useCallback, useState } from "react";
import { getAnalytics, getAnalyticsSessions, type AnalyticsRange } from "@/services/analytics";
import { zonedParts } from "@/features/study-plan/dates";
import { useStudyTimeLoad } from "./use-study-time-load";
export function useAnalyticsData() {
  const [range, setRange] = useState<AnalyticsRange>({ period: 7 }), [offset, setOffset] = useState(0);
  const [custom, setCustom] = useState(false), [start, setStart] = useState(""), [end, setEnd] = useState(""), [dateError, setDateError] = useState<string | null>(null);
  const key = JSON.stringify(range);
  const summary = useStudyTimeLoad(useCallback(async (signal) => ({ key, data: await getAnalytics(range, signal) }), [range, key]));
  const history = useStudyTimeLoad(useCallback(async (signal) => ({ key, offset, data: await getAnalyticsSessions(range, offset, signal) }), [range, key, offset]));
  const data = summary.data?.data ?? null;
  const staleRange = !!summary.data && summary.data.key !== key;
  const sessions = history.data?.data ?? null;
  const historyStale = !!history.data && (history.data.key !== key || history.data.offset !== offset);
  const busy = summary.loading || history.loading;
  const today = summary.data ? zonedParts(new Date(), summary.data.data.timezone).date : "";
  const subjectMaximum = data ? Math.max(0, ...data.subjects.flatMap((subject) => [subject.duration_seconds, subject.planned_seconds])) : 0;
  const activityMaximum = data ? Math.max(0, ...data.activities.map((activity) => activity.duration_seconds)) : 0;
  const plannedMaximum = data ? Math.max(data.summary.total_seconds, data.summary.planned_seconds) : 0;
  const chooseRange = (next: AnalyticsRange) => { setRange(next); setOffset(0); setDateError(null); };
  return { range, offset, custom, setCustom, start, setStart, end, setEnd, dateError, setDateError, summary, history, data, staleRange, sessions, historyStale, busy, today, subjectMaximum, activityMaximum, plannedMaximum, chooseRange, setOffset };
}
export type AnalyticsViewProps = ReturnType<typeof useAnalyticsData>;
