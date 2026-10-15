import { ContentSkeleton } from "@/components/study-ui";

// This boundary replaces only the pending route, never the shared authenticated shell.
export default function Loading() {
  return <ContentSkeleton label="Opening page…" layout="detail" />;
}
