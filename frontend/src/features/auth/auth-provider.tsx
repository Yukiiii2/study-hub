"use client";

import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { authenticatedGet } from "@/services/api";
import { getSupabaseBrowserClient } from "./supabase";
import { initialAuthState, SessionVerifier, type AuthState, type VerifiedUser } from "./session-verification";

const AuthContext = createContext<(AuthState & { retry: () => void }) | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(initialAuthState);
  const verifierRef = useRef<SessionVerifier | null>(null);

  useEffect(() => {
    let active = true;
    let unsubscribe: (() => void) | undefined;
    const verifier = new SessionVerifier((_session, signal) => authenticatedGet<VerifiedUser>("/api/auth/me", signal), setState);
    verifierRef.current = verifier;
    try {
      const supabase = getSupabaseBrowserClient();
      const { data } = supabase.auth.onAuthStateChange((event, session) => {
        if (active) verifier.accept(session, event === "USER_UPDATED");
      });
      unsubscribe = () => data.subscription.unsubscribe();
      // The listener receives INITIAL_SESSION; this also catches storage/init failures.
      void supabase.auth.getSession().then(({ error }) => {
        if (active && error) {
          verifier.fail("Your session could not be restored. Try again.");
        }
      }).catch(() => {
        if (active) verifier.fail("Sign-in service is unavailable. Try again.");
      });
    } catch {
      verifier.fail("Sign-in is not available for this workspace. Contact your workspace administrator.");
    }
    return () => { active = false; unsubscribe?.(); verifier.dispose(); verifierRef.current = null; };
  }, []);

  async function retry() {
    try {
      const { data, error } = await getSupabaseBrowserClient().auth.getSession();
      if (error) verifierRef.current?.fail("Your session could not be restored. Try again.");
      else verifierRef.current?.accept(data.session, true);
    } catch { verifierRef.current?.fail("Sign-in service is unavailable. Try again."); }
  }

  return <AuthContext.Provider value={{ ...state, retry }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const state = useContext(AuthContext);
  if (!state) throw new Error("AuthProvider is required.");
  return state;
}
