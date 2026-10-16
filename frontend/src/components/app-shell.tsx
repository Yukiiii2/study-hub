"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { InterfaceIcon, type IconName } from "@/components/interface-icon";
import { usePageMotion } from "@/components/ui-motion";
import { GlobalAssistant } from "@/features/assistant/global-assistant";

const navigationGroups: { label: string; items: { href: string; label: string; icon: IconName }[] }[] = [
  { label: "Your day", items: [{ href: "/", label: "Today", icon: "calendar" }, { href: "/study-plan", label: "Plan", icon: "calendar" }] },
  { label: "Study", items: [{ href: "/subjects", label: "Subjects", icon: "subjects" }, { href: "/library", label: "Library", icon: "library" }, { href: "/assistant", label: "Assistant", icon: "assistant" }] },
  { label: "Practice", items: [{ href: "/recall", label: "Recall", icon: "recall" }, { href: "/flashcards", label: "Flashcards", icon: "flashcards" }, { href: "/quizzes", label: "Quizzes", icon: "quizzes" }, { href: "/assessments", label: "Assessments", icon: "assessments" }] },
  { label: "Progress", items: [{ href: "/analytics", label: "Analytics", icon: "analytics" }] },
];
function isActive(pathname: string, href: string) {
  return pathname === href || (href !== "/" && pathname.startsWith(`${href}/`)) || (href === "/quizzes" && pathname === "/question-bank");
}
function Navigation() {
  const pathname = usePathname();
  return <nav aria-label="Main navigation">{navigationGroups.map((group) => <div className="nav-group" role="group" aria-label={group.label} key={group.label}>
    <p className="nav-group-label">{group.label}</p>{group.items.map((item) => <Link className={`nav-link${isActive(pathname, item.href) ? " active" : ""}`} href={item.href} aria-current={isActive(pathname, item.href) ? "page" : undefined} title={item.label} key={item.href}><InterfaceIcon name={item.icon} /><span>{item.label}</span></Link>)}
  </div>)}</nav>;
}
export function AppShell({ children, utility }: { children: ReactNode; utility?: ReactNode }) {
  const pathname = usePathname();
  const more = useRef<HTMLDialogElement>(null);
  const moreTrigger = useRef<HTMLButtonElement>(null);
  const moreNavigation = useRef(false);
  const content = useRef<HTMLElement>(null);
  usePageMotion(content, pathname);
  const [moreOpen, setMoreOpen] = useState(false);
  const studyActive = isActive(pathname, "/subjects") || isActive(pathname, "/library");
  const moreActive = !["/", "/study-plan", "/focus"].includes(pathname) && !studyActive;
  const currentTitle = pathname === "/focus" ? "Focus" : pathname === "/settings" ? "Settings" : pathname === "/question-bank" ? "Question Bank" : navigationGroups.flatMap((group) => group.items).find((item) => isActive(pathname, item.href))?.label ?? "Study workspace";
  useEffect(() => {
    if (more.current?.open) { moreNavigation.current = true; more.current.close(); setMoreOpen(false); content.current?.focus(); }
  }, [pathname]);
  return <div className="app-shell" data-page={pathname.split("/")[1] || "today"}>
    <a className="skip-link" href="#main-content">Skip to content</a>
    <aside className="sidebar" aria-label="Study Hub sidebar">
      <div className="workspace-brand"><Link href="/" className="brand"><span className="brand-mark"><InterfaceIcon name="subjects" /></span><span>Study Hub<span className="brand-subtitle">CPALE review workspace</span></span></Link></div>
      <Navigation />
      <Link className={`shell-focus${pathname === "/focus" ? " active" : ""}`} href="/focus" aria-current={pathname === "/focus" ? "page" : undefined}><InterfaceIcon name="focus" /><span><strong>Focus</strong><small>Start a study session</small></span></Link>
      <Link href="/settings" className="shell-settings" aria-current={pathname === "/settings" ? "page" : undefined}><InterfaceIcon name="settings" /><span>Settings</span></Link>
    </aside>
    <div className="workspace">
      <header className="utility-header"><div className="desktop-context"><span>{currentTitle}</span></div><Link className="mobile-brand" href="/"><span className="brand-mark"><InterfaceIcon name="subjects" /></span>Study Hub</Link><span className="mobile-context">{currentTitle}</span><div className="shell-account">{utility}</div></header>
      <main ref={content} id="main-content" tabIndex={-1} className="main-content">{children}</main>
      <nav className="bottom-navigation" aria-label="Mobile navigation">
        {[{ href: "/", label: "Today", icon: "calendar" as const }, { href: "/study-plan", label: "Plan", icon: "calendar" as const }, { href: "/focus", label: "Focus", icon: "focus" as const }, { href: "/subjects", label: "Study", icon: "subjects" as const }].map((item) => <Link href={item.href} key={item.href} className={`bottom-nav-link${item.href === "/focus" ? " bottom-nav-focus" : ""}`} aria-current={(item.href === "/subjects" ? studyActive : isActive(pathname, item.href)) ? "page" : undefined}><InterfaceIcon name={item.icon} /><span>{item.label}</span></Link>)}
        <button ref={moreTrigger} className="bottom-nav-link" aria-current={moreActive ? "page" : undefined} aria-label="More study tools" aria-haspopup="dialog" aria-expanded={moreOpen} onClick={() => { more.current?.showModal(); setMoreOpen(true); }}><InterfaceIcon name="more" /><span>More</span></button>
      </nav>
      <GlobalAssistant />
    </div>
    <dialog ref={more} className="planner-dialog shell-more" aria-labelledby="more-title" onClose={() => { setMoreOpen(false); if (!moreNavigation.current) moreTrigger.current?.focus(); moreNavigation.current = false; }}><header className="planner-dialog-heading"><h2 id="more-title">Study tools</h2><button className="ghost-button" onClick={() => more.current?.close()}>Close</button></header><Navigation /><Link className="nav-link" href="/question-bank"><InterfaceIcon name="quizzes" />Question Bank</Link><Link className="nav-link" href="/settings"><InterfaceIcon name="settings" />Settings</Link></dialog>
  </div>;
}
