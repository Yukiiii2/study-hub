// Calendar arithmetic uses local date strings; instants are converted only at the API boundary.
export function dateAdd(date: string, days: number): string {
  const value = new Date(`${date}T12:00:00Z`);
  value.setUTCDate(value.getUTCDate() + days);
  return value.toISOString().slice(0, 10);
}

export function weekday(date: string): number { return new Date(`${date}T12:00:00Z`).getUTCDay(); }

export function zonedParts(instant: string | Date, timezone: string): { date: string; time: string } {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" }).formatToParts(new Date(instant));
  const part = (name: Intl.DateTimeFormatPartTypes) => parts.find((value) => value.type === name)!.value;
  return { date: `${part("year")}-${part("month")}-${part("day")}`, time: `${part("hour")}:${part("minute")}` };
}

export function localToInstant(date: string, time: string, timezone: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !/^\d{2}:\d{2}$/.test(time)) throw new Error("Enter a valid date and time.");
  const wall = Date.parse(`${date}T${time}:00Z`);
  if (!Number.isFinite(wall) || new Date(wall).toISOString().slice(0, 16) !== `${date}T${time}`) throw new Error("Enter a valid date and time.");
  const offsets = new Set<number>();
  // Sample both sides of a transition, including fractional-hour timezone offsets.
  for (let hours = -48; hours <= 48; hours += 1) {
    const sample = wall + hours * 3600000;
    const local = zonedParts(new Date(sample), timezone);
    offsets.add(Date.parse(`${local.date}T${local.time}:00Z`) - sample);
  }
  const matches = [...offsets].map((offset) => wall - offset).filter((candidate) => {
    const local = zonedParts(new Date(candidate), timezone);
    return local.date === date && local.time === time;
  });
  if (matches.length === 0) throw new Error(`This time does not exist in ${timezone} because the clocks change. Choose another time.`);
  if (matches.length > 1) throw new Error(`This time occurs twice in ${timezone} because the clocks change. Choose an unambiguous time.`);
  return new Date(matches[0]).toISOString();
}

export function calendarDays(date: string, view: "month" | "week"): string[] {
  const first = view === "month" ? `${date.slice(0, 7)}-01` : date;
  const start = dateAdd(first, -((weekday(first) + 6) % 7));
  return Array.from({ length: view === "month" ? 42 : 7 }, (_, index) => dateAdd(start, index));
}

export function dateLabel(date: string, options: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" }): string {
  return new Intl.DateTimeFormat("en", { ...options, timeZone: "UTC" }).format(new Date(`${date}T12:00:00Z`));
}
