import type { Resource } from "@/services/resources";
export const resourceStatus = (resource: Resource) => ({ uploaded: "Uploaded", processing: "Processing", ready: "Ready", failed: "Processing failed" })[resource.processing_status];
export const resourceSize = (bytes: number) => bytes < 1024 ? `${bytes} bytes` : bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} KiB` : `${(bytes / 1048576).toFixed(1)} MiB`;
export function resourceDate(value: string, timezone: string) { return new Intl.DateTimeFormat("en", { timeZone: timezone, month: "short", day: "numeric", year: "numeric" }).format(new Date(value)); }
