import { ApiError } from "@/services/api";
import { assessmentError } from "@/services/assessments";

// The shared quiz loader accepts API errors but has quiz-specific status wording.
// Keep its cancellation/retry behavior while supplying assessment-specific text.
export function assessmentLoad<T>(request: Promise<T>): Promise<T> {
  return request.catch((failure) => { throw new ApiError(assessmentError(failure), 500); });
}
