import type { Session } from "@supabase/supabase-js";

export type VerifiedUser = { id: string; email: string | null };
export type AuthState = {
  session: Session | null;
  user: VerifiedUser | null;
  loading: boolean;
  error: string | null;
};
export const initialAuthState: AuthState = { session: null, user: null, loading: true, error: null };

// One in-memory cache per root provider. Never persist backend validation in storage.
export class SessionVerifier {
  state: AuthState = initialAuthState;
  private token: string | null = null;
  private request: AbortController | null = null;
  private generation = 0;
  private disposed = false;

  constructor(
    private verify: (session: Session, signal: AbortSignal) => Promise<VerifiedUser>,
    private publish: (state: AuthState) => void,
  ) {}

  accept(session: Session | null, force = false) {
    if (this.disposed) return;
    if (!force && session?.access_token === this.token && session?.user.id === this.state.session?.user.id) return;
    this.request?.abort();
    const generation = ++this.generation;
    this.token = session?.access_token ?? null;
    // A refresh retains the verified identity; sign-out/account changes clear it immediately.
    const user = session && session.user.id === this.state.user?.id ? this.state.user : null;
    this.update({ session, user, loading: false, error: null });
    if (!session) return;

    const controller = new AbortController();
    this.request = controller;
    // Leave the Supabase listener callback before invoking SDK-backed requests (auth lock).
    void Promise.resolve().then(() => {
      if (controller.signal.aborted) return null;
      return this.verify(session, controller.signal);
    }).then((verified) => {
      if (controller.signal.aborted || generation !== this.generation || !verified) return;
      if (verified.id !== session.user.id) {
        this.update({ ...this.state, user: null });
        throw new Error("Session identity mismatch");
      }
      this.update({ session: this.state.session, user: verified, loading: false, error: null });
    }).catch((error: unknown) => {
      if (controller.signal.aborted || generation !== this.generation) return;
      if (typeof error === "object" && error !== null && "status" in error && error.status === 401) {
        this.token = null;
        this.update({ session: null, user: null, loading: false, error: null });
      } else {
        this.update({ ...this.state, error: "Could not reach the study service to verify your session. Try again." });
      }
    });
  }

  retry() { this.accept(this.state.session, true); }

  fail(message: string) {
    if (!this.disposed) this.update({ ...this.state, loading: false, error: message });
  }

  dispose() {
    this.disposed = true;
    this.request?.abort();
    this.generation++;
  }

  private update(state: AuthState) { this.state = state; this.publish(state); }
}
