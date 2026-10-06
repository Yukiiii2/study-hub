"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { AppShell } from "@/components/app-shell";
import { DashboardPlaceholder } from "@/features/dashboard/dashboard-placeholder";
import { ApiError, authenticatedGet } from "@/services/api";
import { useAuth } from "./auth-provider";
import { getSupabaseBrowserClient } from "./supabase";

type VerifiedUser = { id: string; email: string | null };
type Verification = { token: string; user: VerifiedUser };

export function ProtectedApp({ children }: { children?: ReactNode }) {
  const { session, loading, error: setupError } = useAuth();
  const router = useRouter();
  const [verification, setVerification] = useState<Verification | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [subjectCount, setSubjectCount] = useState<number | null>(null);
  const [subjectError, setSubjectError] = useState<string | null>(null);
  const [checkingSubjects, setCheckingSubjects] = useState(false);
  const [signingOut, setSigningOut] = useState(false);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    if (loading) return;
    if (!session) { router.replace("/login"); return; }
    const controller = new AbortController();
    setError(null);
    setVerification(null);
    setSubjectCount(null);
    setSubjectError(null);
    void authenticatedGet<VerifiedUser>("/api/auth/me", controller.signal).then((user) => {
      if (!controller.signal.aborted) setVerification({ token: session.access_token, user });
    }).catch((error: unknown) => {
      if (controller.signal.aborted) return;
      if (error instanceof ApiError && error.status === 401) {
        void getSupabaseBrowserClient().auth.signOut({ scope: "local" }).then(({ error }) => {
          if (error) setError("Your session could not be cleared. Try signing out again.");
          else router.replace("/login");
        }).catch(() => setError("Your session could not be cleared. Try signing out again."));
      } else {
        setError(error instanceof ApiError ? error.message : "Could not verify your session. Try again.");
      }
    });
    return () => controller.abort();
  }, [loading, session, router, retry]);

  async function signOut() {
    setSigningOut(true);
    setError(null);
    try {
      // End this browser's session without signing out other devices.
      const { error } = await getSupabaseBrowserClient().auth.signOut({ scope: "local" });
      if (error) setError("Could not sign out. Try again.");
      else router.replace("/login");
    } catch {
      setError("Could not sign out. Try again.");
    } finally { setSigningOut(false); }
  }

  async function checkSubjects() {
    setCheckingSubjects(true);
    setSubjectError(null);
    setSubjectCount(null);
    try {
      const subjects = await authenticatedGet<{ id: string; code: string }[]>("/api/subjects");
      setSubjectCount(subjects.length);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) await signOut();
      else setSubjectError(error instanceof ApiError ? error.message : "Could not check subject setup. Try again.");
    } finally { setCheckingSubjects(false); }
  }

  if (loading || !session || verification?.token !== session.access_token) {
    return (
      <main className="auth-page">
        <section className="auth-panel" aria-label="Session verification">
          <h1>Study Hub</h1>
          {setupError || error ? <>
            <p className="auth-error" role="alert">{setupError || error}</p>
            <div className="auth-actions">
              <button className="secondary-button" onClick={() => setRetry((value) => value + 1)}>Try again</button>
              {session && <button className="secondary-button" onClick={signOut} disabled={signingOut}>Sign out</button>}
            </div>
          </> : <p role="status">{session ? "Verifying your session..." : "Opening sign-in..."}</p>}
        </section>
      </main>
    );
  }

  return (
    <AppShell utility={<div className="account-utility">
      <span className="account-email">{verification.user.email || "Signed in"}</span>
      <button className="secondary-button" onClick={signOut} disabled={signingOut}>
        {signingOut ? "Signing out..." : "Sign out"}
      </button>
    </div>}>
      {error && <p className="auth-error" role="alert">{error}</p>}
      {children ?? <><DashboardPlaceholder />
      <section className="integration-check" aria-label="Subject setup check">
        <button className="secondary-button" onClick={checkSubjects} disabled={checkingSubjects}>
          {checkingSubjects ? "Checking subject setup..." : "Check subject setup"}
        </button>
        {subjectCount !== null && <p role="status">{subjectCount} subject definitions available.</p>}
        {subjectError && <p className="auth-error" role="alert">{subjectError}</p>}
      </section>
      </>}
    </AppShell>
  );
}

export function ProtectedDashboard() {
  return <ProtectedApp />;
}
