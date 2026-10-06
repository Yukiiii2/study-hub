"use client";

import type { Session } from "@supabase/supabase-js";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getSupabaseBrowserClient } from "./supabase";

type AuthState = { session: Session | null; loading: boolean; error: string | null };
const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ session: null, loading: true, error: null });

  useEffect(() => {
    let active = true;
    let unsubscribe: (() => void) | undefined;
    try {
      const supabase = getSupabaseBrowserClient();
      const { data } = supabase.auth.onAuthStateChange((_event, session) => {
        if (active) setState({ session, loading: false, error: null });
      });
      unsubscribe = () => data.subscription.unsubscribe();
      // The listener receives INITIAL_SESSION; this also catches storage/init failures.
      void supabase.auth.getSession().then(({ error }) => {
        if (active && error) {
          setState({ session: null, loading: false, error: "Your session could not be restored. Please sign in again." });
        }
      }).catch(() => {
        if (active) setState({ session: null, loading: false, error: "Sign-in service is unavailable. Try again." });
      });
    } catch {
      setState({ session: null, loading: false, error: "Sign-in is not configured. Set the public Supabase environment values." });
    }
    return () => { active = false; unsubscribe?.(); };
  }, []);

  return <AuthContext.Provider value={state}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const state = useContext(AuthContext);
  if (!state) throw new Error("AuthProvider is required.");
  return state;
}
