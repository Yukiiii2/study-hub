import { getSupabaseBrowserClient } from "@/features/auth/supabase";
import { config } from "@/lib/config";
import type { AuthError, Session, SupabaseClient } from "@supabase/supabase-js";

let refresh: { token: string; userId: string; promise: ReturnType<SupabaseClient["auth"]["refreshSession"]> } | null = null;

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) { super(message); }
}

export async function authenticatedGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  return authenticatedRequest<T>(path, "GET", undefined, signal);
}

export async function authenticatedPatch<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  return authenticatedRequest<T>(path, "PATCH", body, signal);
}

export async function authenticatedPost<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  return authenticatedRequest<T>(path, "POST", body, signal);
}

export async function authenticatedDelete(path: string, signal?: AbortSignal): Promise<void> {
  return authenticatedRequest<void>(path, "DELETE", undefined, signal);
}

async function authenticatedRequest<T>(path: string, method: "GET" | "PATCH" | "POST" | "DELETE", body?: unknown, signal?: AbortSignal): Promise<T> {
  if (!config.apiUrl) throw new ApiError("The study service is not configured.", 503);
  const auth = getSupabaseBrowserClient().auth;
  const session = await currentSession();

  async function send(token: string) {
    try {
      return await fetch(`${config.apiUrl}${path}`, {
        method,
        headers: { Authorization: `Bearer ${token}`, ...(body === undefined ? {} : { "Content-Type": "application/json" }) },
        body: body === undefined ? undefined : JSON.stringify(body),
        cache: "no-store",
        signal,
      });
    } catch (error) {
      if (signal?.aborted) throw error;
      throw new ApiError("The study service is unavailable. Try again.", 503);
    }
  }
  let response = await send(session.access_token);
  if (response.status === 401) {
    signal?.throwIfAborted();
    // getSession performs the SDK's normal expired-token recovery. Reuse a newer token.
    let recovered = await currentSession();
    if (recovered.user.id !== session.user.id) throw new ApiError("The signed-in account changed. Try again.", 401);
    if (recovered.access_token === session.access_token) {
      const pending = refresh?.token === session.access_token && refresh.userId === session.user.id
        ? refresh : { token: session.access_token, userId: session.user.id, promise: auth.refreshSession() };
      refresh = pending;
      let result;
      try { result = await pending.promise; }
      catch {
        signal?.throwIfAborted();
        throw new ApiError("Sign-in is temporarily unavailable. Try again.", 503);
      } finally { if (refresh === pending) refresh = null; }
      signal?.throwIfAborted();
      if (result.error) {
        const failure = authFailure(result.error);
        if (failure.status === 401) await clearRejectedSession(session, signal);
        throw failure;
      }
      if (!result.data.session) throw new ApiError("Your session has expired. Please sign in again.", 401);
      recovered = result.data.session;
    }
    signal?.throwIfAborted();
    const current = await currentSession();
    if (current.user.id !== session.user.id) throw new ApiError("The signed-in account changed. Try again.", 401);
    recovered = current;
    response = await send(recovered.access_token);
    if (response.status === 401) {
      await clearRejectedSession(recovered, signal);
      throw new ApiError("Your session could not be verified. Please sign in again.", 401);
    }
  }
  if (!response.ok) throw new ApiError("The study service could not complete the request. Try again.", response.status);
  if (response.status === 204) return undefined as T;
  try {
    return await response.json() as T;
  } catch {
    throw new ApiError("The study service returned an unreadable response. Try again.", 502);
  }
}

function authFailure(error: AuthError): ApiError {
  const invalid = error.status === 400 || error.status === 401 || error.status === 403 || error.status === 422;
  return new ApiError(invalid ? "Your session has expired. Please sign in again." : "Sign-in is temporarily unavailable. Try again.", invalid ? 401 : 503);
}

async function currentSession(): Promise<Session> {
  let result;
  try { result = await getSupabaseBrowserClient().auth.getSession(); }
  catch { throw new ApiError("Sign-in is temporarily unavailable. Try again.", 503); }
  if (result.error) throw authFailure(result.error);
  if (!result.data.session) throw new ApiError("Your session has expired. Please sign in again.", 401);
  return result.data.session;
}

async function clearRejectedSession(rejected: Session, signal?: AbortSignal) {
  signal?.throwIfAborted();
  const { data, error } = await getSupabaseBrowserClient().auth.getSession();
  signal?.throwIfAborted();
  // A delayed response must never sign out a replacement session/account.
  if (error) throw authFailure(error);
  if (data.session && (data.session.user.id !== rejected.user.id || data.session.access_token !== rejected.access_token)) {
    throw new ApiError("Your session changed while checking the request. Try again.", 503);
  }
  if (data.session) await getSupabaseBrowserClient().auth.signOut({ scope: "local" });
}
