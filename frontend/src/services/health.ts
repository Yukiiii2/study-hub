import { config } from "@/lib/config";

export async function getHealth(signal?: AbortSignal): Promise<{ status: "ok" }> {
  if (!config.apiUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is not configured.");
  }

  const response = await fetch(`${config.apiUrl}/health`, {
    cache: "no-store",
    signal,
  });
  if (!response.ok) {
    throw new Error(`Health request failed (${response.status}).`);
  }

  const data: unknown = await response.json();
  if (typeof data !== "object" || data === null || !("status" in data) || data.status !== "ok") {
    throw new Error("Unexpected health response.");
  }
  return { status: "ok" };
}
