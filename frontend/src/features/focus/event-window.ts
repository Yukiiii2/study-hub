import { dateAdd, zonedParts } from "@/features/study-plan/dates";

// This is a conservative read envelope, not a scheduled wall-clock instant.
// Local midnight can be repeated or absent, so it must not use form validation.
export function focusEventWindow(today: string) {
  const endDate = dateAdd(today, 8);
  const margin = 26 * 3600000;
  return {
    startAt: new Date(Date.parse(`${today}T00:00:00Z`) - margin).toISOString(),
    endAt: new Date(Date.parse(`${endDate}T00:00:00Z`) + margin).toISOString(),
    endDate,
  };
}

export function eventOverlapsFocusDates(event: { start_at: string; end_at: string }, today: string, endDate: string, timezone: string) {
  const startDate = zonedParts(event.start_at, timezone).date;
  // The API interval is half-open: an event ending exactly at the first local
  // midnight has no activity on that day, including a repeated midnight.
  const lastDate = zonedParts(new Date(Date.parse(event.end_at) - 1), timezone).date;
  return startDate < endDate && lastDate >= today;
}
