"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { AccountMenu } from "@/components/account-menu";
import { AppShell } from "@/components/app-shell";
import { useAuth } from "./auth-provider";
import { getSupabaseBrowserClient } from "./supabase";

// Mounted once in the shared protected route layout, never once per page.
export function ProtectedApp({ children }: { children: ReactNode }) {
  const { session, user, loading, error, retry } = useAuth();
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);
  const [signOutError, setSignOutError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && !session && !error) router.replace("/login");
  }, [loading, session, error, router]);

  async function signOut() {
    setSigningOut(true);
    setSignOutError(null);
    try {
      const { error } = await getSupabaseBrowserClient().auth.signOut({ scope: "local" });
      if (error) setSignOutError("Could not sign out. Try again.");
      else router.replace("/login");
    } catch { setSignOutError("Could not sign out. Try again."); }
    finally { setSigningOut(false); }
  }

  if (loading || !session || !user) {
    return (
      <main className="auth-page">
        <section className="auth-bootstrap" aria-label="Session verification">
          <p className="brand">Study Hub</p>
          {error || signOutError ? <>
            <p className="auth-error" role="alert">{error || signOutError}</p>
            <div className="auth-actions">
              <button className="secondary-button" onClick={retry}>Try again</button>
              {session && <button className="secondary-button" onClick={signOut} disabled={signingOut}>Sign out</button>}
            </div>
          </> : <>
            <div className="auth-bootstrap-skeleton" aria-hidden="true" />
            <p role="status">{loading || session ? "Opening your workspace…" : "Opening sign-in…"}</p>
          </>}
        </section>
      </main>
    );
  }

  return (
    <AppShell utility={<AccountMenu email={user.email} signingOut={signingOut} signOut={() => void signOut()} />}>
      {(error || signOutError) && <div className="auth-actions">
        <p className="auth-error" role="alert">{error || signOutError}</p>
        {error && <button className="secondary-button" onClick={retry}>Retry connection</button>}
      </div>}
      {children}
    </AppShell>
  );
}
