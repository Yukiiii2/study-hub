import type { LabeledSession } from "@/services/analytics";
import { studyDuration } from "./presentation";

export function SessionList({ sessions, timezone }: { sessions: LabeledSession[]; timezone: string }) {
  const timestamp = (value: string) => new Intl.DateTimeFormat("en", { timeZone: timezone, month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(value));
  return <ul className="quiz-list study-session-list">{sessions.map((session) => <li className="quiz-row" key={session.id}>
    <div className="quiz-row-copy"><strong>{session.subject_code ?? "No subject"}{session.topic_title ? ` — ${session.topic_title}` : ""}</strong><span>{session.activity_type} · <time dateTime={session.started_at}>{timestamp(session.started_at)}</time>{session.ended_at && <> to <time dateTime={session.ended_at}>{timestamp(session.ended_at)}</time></>}</span>{session.notes && <span className="study-session-notes">{session.notes}</span>}</div>
    <span className="study-session-duration">{session.duration_seconds === null ? "In progress" : studyDuration(session.duration_seconds)}</span>
  </li>)}</ul>;
}
