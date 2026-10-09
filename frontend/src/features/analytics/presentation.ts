export function studyDuration(seconds: number): string {
  const value = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(value / 3600), minutes = Math.floor(value % 3600 / 60), remainder = value % 60;
  return `${hours}:${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
}
export type ClockAnchor = { serverTime: number; monotonicTime: number };
export function elapsedSeconds(startedAt: string, anchor: ClockAnchor, monotonicNow: number): number {
  return Math.max(0, Math.floor((anchor.serverTime + Math.max(0, monotonicNow - anchor.monotonicTime) - Date.parse(startedAt)) / 1000));
}
export function rangeError(start: string, end: string, today: string): string | null {
  const parse = (value: string) => /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(`${value}T12:00:00Z`)) && new Date(`${value}T12:00:00Z`).toISOString().slice(0, 10) === value;
  if (!parse(start) || !parse(end)) return "Choose both a valid start date and end date.";
  if (start > end) return "The start date must be on or before the end date.";
  if (end > today) return "The end date cannot be in the future.";
  if ((Date.parse(`${end}T12:00:00Z`) - Date.parse(`${start}T12:00:00Z`)) / 86400000 + 1 > 90) return "Choose a range of at most 90 days, including both dates.";
  return null;
}
