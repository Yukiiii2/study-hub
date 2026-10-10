import { ApiError } from "@/services/api";

export function aiCardSaveOutcomeUnknown(error: unknown) {
  return !(error instanceof ApiError) || error.status >= 500;
}
