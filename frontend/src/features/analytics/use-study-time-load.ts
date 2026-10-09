import { useEffect, useState } from "react";
import { studyTimeError } from "@/services/analytics";

export function useStudyTimeLoad<T>(loader: (signal: AbortSignal) => Promise<T>) {
  const [data, setData] = useState<T | null>(null), [loading, setLoading] = useState(true), [error, setError] = useState<string | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true); setError(null);
    void loader(controller.signal).then((value) => { if (!controller.signal.aborted) setData(value); }).catch((failure) => { if (!controller.signal.aborted) setError(studyTimeError(failure)); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [loader, revision]);
  return { data, loading, error, retry: () => setRevision((value) => value + 1) };
}
