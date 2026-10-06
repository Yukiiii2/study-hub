"use client";

import { useEffect, useState } from "react";
import { ApiError } from "@/services/api";
import { getDashboard, type DashboardData } from "@/services/dashboard";
import { DashboardView } from "./dashboard-view";

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(true);
  const [revision, setRevision] = useState(0);

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

  return <DashboardView data={data} error={error} refreshing={refreshing} onRefresh={() => setRevision((value) => value + 1)} />;
}
