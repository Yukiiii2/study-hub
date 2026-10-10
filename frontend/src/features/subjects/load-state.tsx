export function CurriculumLoading() {
  return <div className="curriculum-loading" role="status" aria-live="polite">
    <span>Loading study data...</span>
    <div className="skeleton-row" aria-hidden="true" />
    <div className="skeleton-row" aria-hidden="true" />
    <div className="skeleton-row" aria-hidden="true" />
  </div>;
}

export function CurriculumError({ message, retry }: { message: string; retry: () => void }) {
  return <div className="curriculum-state">
    <h2>Study data is unavailable</h2>
    <p className="auth-error" role="alert">{message}</p>
    <button className="secondary-button" onClick={retry}>Try again</button>
  </div>;
}
