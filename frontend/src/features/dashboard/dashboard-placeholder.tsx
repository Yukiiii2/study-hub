export function DashboardPlaceholder() {
  return (
    <>
      <div className="page-heading">
        <h1>Dashboard</h1>
        <p>A home for your CPALE review.</p>
      </div>
      <section className="dashboard-placeholder" aria-labelledby="placeholder-title">
        <div className="placeholder-content">
          <h2 id="placeholder-title">Your study workspace starts here.</h2>
          <p>
            Your study plan, subject progress, and upcoming reviews will have a
            place here as Study Hub takes shape.
          </p>
          <p className="placeholder-note">
            This is the foundation preview. Study tools and account setup are
            not available yet.
          </p>
        </div>
      </section>
    </>
  );
}
