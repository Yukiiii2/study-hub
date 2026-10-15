import { ContentSkeleton, type SkeletonLayout } from "@/components/study-ui";

export function CurriculumLoading({ layout = "rows" }: { layout?: SkeletonLayout }) {
  return <ContentSkeleton label="Loading study data…" layout={layout} />;
}

export function CurriculumError({ message, retry }: { message: string; retry: () => void }) {
  return <div className="curriculum-state">
    <h2>Study data is unavailable</h2>
    <p className="auth-error" role="alert">{message}</p>
    <button className="secondary-button" onClick={retry}>Try again</button>
  </div>;
}
