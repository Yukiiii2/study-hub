"use client";

import Link from "next/link";
import { useRef } from "react";

export function AccountMenu({ email, signingOut, signOut }: {
  email: string | null; signingOut: boolean; signOut: () => void;
}) {
  const menu = useRef<HTMLDetailsElement>(null);
  return <details className="account-menu" ref={menu} onBlur={(event) => {
    if (!event.currentTarget.contains(event.relatedTarget)) event.currentTarget.open = false;
  }} onKeyDown={(event) => {
    if (event.key === "Escape" && menu.current?.open) {
      event.preventDefault(); menu.current.open = false; menu.current.querySelector("summary")?.focus();
    }
  }}>
    <summary>Account</summary>
    <div className="account-menu-panel"><p className="account-menu-label">Signed in</p><p className="account-menu-email">{email || "Study Hub account"}</p>
      <Link className="ghost-button" href="/settings" onClick={() => { if (menu.current) menu.current.open = false; }}>Account settings</Link>
      <button className="secondary-button" onClick={signOut} disabled={signingOut}>{signingOut ? "Signing out..." : "Sign out"}</button>
    </div>
  </details>;
}
