"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const plannedAreas = [
  "Recall", "Flashcards",
  "Assessments", "Analytics", "Settings",
];

function Navigation() {
  const pathname = usePathname();
  const subjectsActive = pathname === "/subjects" || pathname.startsWith("/subjects/");
  const libraryActive = pathname === "/library" || pathname.startsWith("/library/");
  const quizzesActive = pathname === "/quizzes" || pathname.startsWith("/quizzes/") || pathname === "/question-bank";
  return (
    <nav aria-label="Main navigation">
      <Link className={`nav-link${pathname === "/" ? " active" : ""}`} href="/" aria-current={pathname === "/" ? "page" : undefined}>
        Dashboard
      </Link>
      <Link className={`nav-link${pathname === "/study-plan" ? " active" : ""}`} href="/study-plan" aria-current={pathname === "/study-plan" ? "page" : undefined}>
        Study Plan
      </Link>
      <Link className={`nav-link${subjectsActive ? " active" : ""}`} href="/subjects" aria-current={subjectsActive ? "page" : undefined}>
        Subjects
      </Link>
      <Link className={`nav-link${libraryActive ? " active" : ""}`} href="/library" aria-current={libraryActive ? "page" : undefined}>
        Library
      </Link>
      <Link className={`nav-link${quizzesActive ? " active" : ""}`} href="/quizzes" aria-current={quizzesActive ? "page" : undefined}>
        Quizzes
      </Link>
      <p className="nav-caption">Planned areas</p>
      <ul className="planned-nav" aria-label="Planned areas">
        {plannedAreas.map((label) => (
          <li key={label}>
            <span className="nav-link" aria-disabled="true">{label}</span>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function AppShell({ children, utility }: { children: ReactNode; utility?: ReactNode }) {
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
          {utility ?? <span className="phase-label">Study workspace</span>}
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
