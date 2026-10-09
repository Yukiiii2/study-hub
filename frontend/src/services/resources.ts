import { ApiError, authenticatedDelete, authenticatedGet, authenticatedPost } from "./api";

export type Resource = {
  id: string; subject_id: string | null; topic_id: string | null; subject_code: string | null; topic_title: string | null;
  title: string; original_filename: string; mime_type: string; file_size_bytes: number; resource_type: "pdf" | "csv";
  processing_status: "uploaded" | "processing" | "ready" | "failed"; page_count: number | null; row_count: number | null;
  error_message: string | null; created_at: string; updated_at: string;
};
export type ResourceList = { resources: Resource[]; total: number };
export type ResourceContent = { resource: Resource; sections: { id: string; page_number: number; section_index: number; content: string }[]; headers: string[]; rows: string[][]; row_count: number | null; total_sections: number };
export type ResourceFilters = { subject_id?: string; resource_type?: string; q?: string; offset: number; limit: number };
const base = "/api/resources";
const resourcePath = (id: string) => `${base}/${encodeURIComponent(id)}`;
export function getResources(filters: ResourceFilters, signal?: AbortSignal) {
  const params = new URLSearchParams({ limit: String(filters.limit), offset: String(filters.offset) });
  for (const key of ["subject_id", "resource_type", "q"] as const) if (filters[key]) params.set(key, filters[key]);
  return authenticatedGet<ResourceList>(`${base}?${params}`, signal);
}
export const getResource = (id: string, signal?: AbortSignal) => authenticatedGet<Resource>(resourcePath(id), signal);
export const getResourceContent = (id: string, offset = 0, signal?: AbortSignal) => authenticatedGet<ResourceContent>(`${resourcePath(id)}/content?limit=10&offset=${offset}`, signal);
export const deleteResource = (id: string) => authenticatedDelete(resourcePath(id));
export const getResourceLink = (id: string, download = true) => authenticatedGet<{ url: string; expires_in: number }>(`${resourcePath(id)}/download?download=${download}`);
export function uploadResource(file: File, title: string, subject: string, topic: string) {
  const body = new FormData(); body.append("file", file);
  if (title.trim()) body.append("title", title.trim());
  if (subject) body.append("subject_id", subject);
  if (topic) body.append("topic_id", topic);
  return authenticatedPost<Resource>(`${base}/upload`, body);
}
export function uploadFileError(file: Pick<File, "name" | "size">): string | null {
  if (!/\.(pdf|csv)$/i.test(file.name)) return "Choose a PDF or CSV file.";
  if (file.size > 4_194_304) return "Choose a file no larger than 4 MiB.";
  if (file.size === 0) return "This file is empty. Choose a file with content.";
  return null;
}
export function resourceError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 404) return "This resource is no longer available. Refresh the library.";
    if (error.status === 413) return "Choose a file no larger than 4 MiB.";
    if (error.status === 415) return "Choose a supported PDF or CSV file. Its contents must match the file type.";
    if (error.status === 422) return error.message === "Choose an active subject and its matching topic." || /^(CSV |Invalid CSV )/.test(error.message) ? error.message : "Check the file, title and subject/topic selection. CSV files need a header and consistent columns.";
    return error.message;
  }
  return "The resource request failed. Try again.";
}

const safeProcessingErrors = new Set([
  "Password-protected PDFs cannot be processed.", "PDF processing supports 1 to 200 pages.",
  "PDF page content exceeds the processing limit.", "PDF extracted text exceeds the processing limit.",
  "No selectable text was found. OCR is not supported.", "PDF text extraction failed. The original file is available.",
]);
export function resourceProcessingError(resource: Resource) {
  return resource.error_message && safeProcessingErrors.has(resource.error_message) ? resource.error_message : "The original file was saved, but its text could not be extracted.";
}
