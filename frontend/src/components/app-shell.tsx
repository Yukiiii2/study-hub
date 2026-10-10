"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, type ReactNode } from "react";
import { InterfaceIcon, type IconName } from "@/components/interface-icon";

const navigationGroups: { label: string; items: { href: string; label: string; icon: IconName }[] }[] = [
  { label: "Workspace", items: [
    { href: "/", label: "Dashboard", icon: "dashboard" },
    { href: "/study-plan", label: "Study Plan", icon: "calendar" },
    { href: "/focus", label: "Focus", icon: "focus" },
  ] },
  { label: "Study tools", items: [
    { href: "/subjects", label: "Subjects", icon: "subjects" },
    { href: "/library", label: "Library", icon: "library" },
    { href: "/quizzes", label: "Quizzes", icon: "quizzes" },
    { href: "/recall", label: "Recall", icon: "recall" },
    { href: "/flashcards", label: "Flashcards", icon: "flashcards" },
    { href: "/assessments", label: "Assessments", icon: "assessments" },
  ] },
  { label: "Insights", items: [
    { href: "/analytics", label: "Analytics", icon: "analytics" },
    { href: "/assistant", label: "Study assistant", icon: "assistant" },
  ] },
];

function isActive(pathname: string, href: string) {
  return pathname === href || (href !== "/" && pathname.startsWith(`${href}/`)) || (href === "/quizzes" && pathname === "/question-bank");
}

function Navigation() {
  const pathname = usePathname();
  return (
    <nav aria-label="Main navigation">
      {navigationGroups.map((group) => <div className="nav-group" role="group" aria-label={group.label} key={group.label}>
        <p className="nav-group-label">{group.label}</p>
        {group.items.map((item) => {
          const active = isActive(pathname, item.href);
          return <Link className={`nav-link${active ? " active" : ""}`} href={item.href} aria-current={active ? "page" : undefined} key={item.href}>
            <InterfaceIcon name={item.icon} /><span>{item.label}</span>
          </Link>;
        })}
      </div>)}
    </nav>
  );
}

export function AppShell({ children, utility }: { children: ReactNode; utility?: ReactNode }) {
  const pathname = usePathname();
  const currentTitle = pathname === "/question-bank" ? "Question Bank" : navigationGroups.flatMap((group) => group.items).find((item) => isActive(pathname, item.href))?.label ?? "Study workspace";
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
        <Link href="/" className="brand"><span className="brand-mark"><InterfaceIcon name="subjects" /></span>Study Hub</Link>
        <p className="workspace-label">CPALE workspace</p>
        <Navigation />
      </aside>
      <div className="workspace">
        <header className="utility-header">
          <div className="desktop-context"><Link href="/">Workspace</Link><span aria-hidden="true">/</span><span>{currentTitle}</span></div>
          <Link className="mobile-brand" href="/">Study Hub</Link>
          {utility ?? <span className="phase-label">Study workspace</span>}
        </header>
        <details ref={navigation} className="mobile-navigation" onKeyDown={(event) => {
          if (event.key === "Escape" && navigation.current?.open) {
            event.preventDefault();
            navigation.current.open = false;
            navigation.current.querySelector("summary")?.focus();
          }
        }}>
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
