"use client";

import { useEffect, useState } from "react";
import { getPlannerContext } from "@/services/study-plan";

export function useResourceTimezone() {
  const [timezone, setTimezone] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setFailed(false);
    void getPlannerContext(controller.signal).then((context) => { if (!controller.signal.aborted) setTimezone(context.timezone); }).catch(() => { if (!controller.signal.aborted) setFailed(true); });
    return () => controller.abort();
  }, [retry]);
  return { timezone: timezone ?? "Asia/Manila", timezoneNote: timezone ? `Dates use ${timezone}.` : `Dates use Asia/Manila until your profile timezone is available.`, timezoneFailed: failed, retryTimezone: () => setRetry((value) => value + 1) };
}
