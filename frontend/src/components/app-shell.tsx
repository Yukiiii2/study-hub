"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, type ReactNode } from "react";

function Navigation() {
  const pathname = usePathname();
  const subjectsActive = pathname === "/subjects" || pathname.startsWith("/subjects/");
  const libraryActive = pathname === "/library" || pathname.startsWith("/library/");
  const quizzesActive = pathname === "/quizzes" || pathname.startsWith("/quizzes/") || pathname === "/question-bank";
  const flashcardsActive = pathname === "/flashcards" || pathname.startsWith("/flashcards/");
  const assessmentsActive = pathname === "/assessments" || pathname.startsWith("/assessments/");
  return (
    <nav aria-label="Main navigation">
      <Link className={`nav-link${pathname === "/" ? " active" : ""}`} href="/" aria-current={pathname === "/" ? "page" : undefined}>
        Dashboard
      </Link>
      <Link className={`nav-link${pathname === "/study-plan" ? " active" : ""}`} href="/study-plan" aria-current={pathname === "/study-plan" ? "page" : undefined}>
        Study Plan
      </Link>
      <Link className={`nav-link${pathname === "/focus" ? " active" : ""}`} href="/focus" aria-current={pathname === "/focus" ? "page" : undefined}>Focus</Link>
      <Link className={`nav-link${subjectsActive ? " active" : ""}`} href="/subjects" aria-current={subjectsActive ? "page" : undefined}>
        Subjects
      </Link>
      <Link className={`nav-link${libraryActive ? " active" : ""}`} href="/library" aria-current={libraryActive ? "page" : undefined}>
        Library
      </Link>
      <Link className={`nav-link${quizzesActive ? " active" : ""}`} href="/quizzes" aria-current={quizzesActive ? "page" : undefined}>
        Quizzes
      </Link>
      <Link className={`nav-link${pathname === "/recall" ? " active" : ""}`} href="/recall" aria-current={pathname === "/recall" ? "page" : undefined}>
        Recall
      </Link>
      <Link className={`nav-link${flashcardsActive ? " active" : ""}`} href="/flashcards" aria-current={flashcardsActive ? "page" : undefined}>
        Flashcards
      </Link>
      <Link className={`nav-link${assessmentsActive ? " active" : ""}`} href="/assessments" aria-current={assessmentsActive ? "page" : undefined}>
        Assessments
      </Link>
      <Link className={`nav-link${pathname === "/analytics" ? " active" : ""}`} href="/analytics" aria-current={pathname === "/analytics" ? "page" : undefined}>Analytics</Link>
      <Link className={`nav-link${pathname === "/assistant" ? " active" : ""}`} href="/assistant" aria-current={pathname === "/assistant" ? "page" : undefined}>Study assistant</Link>
    </nav>
  );
}

export function AppShell({ children, utility }: { children: ReactNode; utility?: ReactNode }) {
  const pathname = usePathname();
  const navigation = useRef<HTMLDetailsElement>(null);
  const content = useRef<HTMLElement>(null);
  useEffect(() => {
    if (navigation.current?.open) {
      navigation.current.open = false;
      content.current?.focus();
    }
  }, [pathname]);
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
        <details ref={navigation} className="mobile-navigation">
          <summary>Navigation</summary>
          <Navigation />
        </details>
        <main ref={content} id="main-content" tabIndex={-1} className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
