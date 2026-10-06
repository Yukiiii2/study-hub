"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "./auth-provider";
import { getSupabaseBrowserClient } from "./supabase";

export function LoginForm() {
  const { session, loading, error: setupError } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && session) router.replace("/");
  }, [loading, session, router]);

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setError(null);
    try {
      const { error } = await getSupabaseBrowserClient().auth.signInWithPassword({
        email: String(form.get("email")).trim(),
        password: String(form.get("password")),
      });
      if (error) {
        setError(error.status === 400 || error.status === 401 || error.status === 422
          ? "Sign-in failed. Check your email and password, and confirm your account is enabled."
          : "Sign-in is temporarily unavailable. Try again.");
        return;
      }
      router.replace("/");
    } catch {
      setError("Could not reach the sign-in service. Check your connection and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="login-title">
        <p className="brand">Study Hub</p>
        <h1 id="login-title">Sign in to your workspace</h1>
        <p className="auth-description">Continue your CPALE review.</p>
        <form onSubmit={signIn} className="auth-form">
          <label htmlFor="email">Email</label>
          <input id="email" name="email" type="email" autoComplete="username" required disabled={submitting} />
          <label htmlFor="password">Password</label>
          <input id="password" name="password" type="password" autoComplete="current-password" required disabled={submitting} />
          {(setupError || error) && <p className="auth-error" role="alert">{setupError || error}</p>}
          <button className="primary-button" type="submit" disabled={loading || submitting || Boolean(setupError)}>
            {loading ? "Restoring session..." : submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="auth-note">Use the account provided for your study workspace.</p>
      </section>
    </main>
  );
}
