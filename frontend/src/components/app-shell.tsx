import Link from "next/link";
import type { ReactNode } from "react";

const plannedAreas = [
  "Study Plan", "Subjects", "Recall", "Flashcards", "Quizzes",
  "Library", "Assessments", "Analytics", "Settings",
];

function Navigation() {
  return (
    <nav aria-label="Main navigation">
      <Link className="nav-link active" href="/" aria-current="page">
        Dashboard
      </Link>
      <p className="nav-caption">Planned areas</p>
      <ul className="planned-nav" aria-label="Planned areas">
        {plannedAreas.map((label) => (
          <li key={label}>
            <span className="nav-link" aria-disabled="true">{label}</span>
          </li>
        ))}
      </ul>
      <p className="nav-note">Planned areas are not available yet.</p>
    </nav>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to content</a>
      <aside className="sidebar" aria-label="Study Hub sidebar">
        <Link href="/" className="brand">Study Hub</Link>
        <p className="workspace-label">CPALE workspace</p>
        <Navigation />
        <p className="sidebar-footer">Your review, in one place.</p>
      </aside>
      <div className="workspace">
        <header className="utility-header">
          <span className="desktop-context">CPALE review</span>
          <Link className="mobile-brand" href="/">Study Hub</Link>
          <span className="phase-label">Foundation preview</span>
        </header>
        <details className="mobile-navigation">
          <summary>Navigation</summary>
          <Navigation />
        </details>
        <main id="main-content" tabIndex={-1} className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
