import { getSupabaseBrowserClient } from "@/features/auth/supabase";
import { config } from "@/lib/config";

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) { super(message); }
}

export async function authenticatedGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  if (!config.apiUrl) throw new ApiError("The study service is not configured.", 503);
  const { data, error } = await getSupabaseBrowserClient().auth.getSession();
  if (error || !data.session) throw new ApiError("Your session has expired. Please sign in again.", 401);

  let response: Response;
  try {
    response = await fetch(`${config.apiUrl}${path}`, {
      headers: { Authorization: `Bearer ${data.session.access_token}` },
      cache: "no-store",
      signal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new ApiError("The study service is unavailable. Try again.", 503);
  }
  if (response.status === 401) throw new ApiError("Your session could not be verified. Please sign in again.", 401);
  if (!response.ok) throw new ApiError("The study service could not complete the request. Try again.", response.status);
  try {
    return await response.json() as T;
  } catch {
    throw new ApiError("The study service returned an unreadable response. Try again.", 502);
  }
}
