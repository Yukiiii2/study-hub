import Link from "next/link";
import type { DashboardData } from "@/services/dashboard";
import { CurriculumLoading } from "@/features/subjects/load-state";
import { dateLabel, zonedParts } from "@/features/study-plan/dates";
import { formatDuration } from "@/features/videos/duration";

type Props = { data: DashboardData | null; refreshing: boolean; error: string | null; onRefresh: () => void };

export function DashboardView({ data, refreshing, error, onRefresh }: Props) {
  const videoSubject = data?.continue_video_subject_id ?? data?.subjects.find((subject) => subject.video_count > 0)?.id;
  const videoPath = videoSubject ? `/subjects/${encodeURIComponent(videoSubject)}/videos` : null;
  const subjectColors = new Map(data?.subjects.map((subject) => [subject.id, subject.color_key]));
  const summary = data?.video_summary;

  function eventTime(instant: string) {
    const parts = zonedParts(instant, data!.timezone);
    return parts.date === data!.date ? parts.time : `${dateLabel(parts.date)} ${parts.time}`;
  }

  return <>
    <header className="page-heading dashboard-heading">
      <div><h1>Dashboard</h1><p>{data ? dateLabel(data.date, { weekday: "long", month: "long", day: "numeric", year: "numeric" }) : "Your review at a glance."}</p></div>
      <button type="button" className="secondary-button" disabled={refreshing} onClick={onRefresh}>
        {refreshing ? "Refreshing…" : "Refresh"}
      </button>
    </header>
    <nav className="dashboard-actions" aria-label="Quick actions">
      <Link className="primary-button" href="/study-plan">Open Study Plan</Link>
      <Link className="secondary-button" href="/subjects">Browse Subjects</Link>
      {videoPath && <Link className="secondary-button" href={videoPath}>{data?.continue_video_subject_id ? "Continue Videos" : "Browse Videos"}</Link>}
    </nav>
    {error && <p className="auth-error dashboard-error" role="alert">{error} {data && "Showing the last loaded dashboard."} Use Refresh to try again.</p>}
    {data === null ? !error && <CurriculumLoading /> : <div className="dashboard-grid" aria-busy={refreshing}>
      <section className="dashboard-section dashboard-today" aria-labelledby="dashboard-today">
        <header className="dashboard-section-heading"><h2 id="dashboard-today">Today</h2><Link href="/study-plan">Study Plan</Link></header>
        <p className="dashboard-section-note">Times in {data.timezone}</p>
        {data.today_events.length === 0 ? <div className="dashboard-empty"><p>No study events today.</p><span>Open Study Plan to add a study block or schedule a task.</span></div> :
          <ul className="dashboard-event-list">{data.today_events.map((event) => <li className="dashboard-event" key={`${event.id}/${event.occurrence_date ?? "one"}`}>
            <div className="dashboard-event-time"><time dateTime={event.start_at}>{eventTime(event.start_at)}</time><span>– <time dateTime={event.end_at}>{eventTime(event.end_at)}</time></span></div>
            <span className="subject-marker" data-color={subjectColors.get(event.subject_id ?? "") ?? undefined} aria-hidden="true" />
            <div className="dashboard-item-copy"><h3>{event.title}</h3><p>{event.subject_code ?? "General study"}{event.topic_title && ` · ${event.topic_title}`}</p>{event.is_recurring && <span className="dashboard-recurrence">Repeats</span>}</div>
            <span className="dashboard-event-status" data-status={event.status}>{event.status[0].toUpperCase() + event.status.slice(1)}</span>
          </li>)}</ul>}
      </section>

      <section className="dashboard-section dashboard-tasks" aria-labelledby="dashboard-tasks">
        <header className="dashboard-section-heading"><h2 id="dashboard-tasks">Upcoming tasks</h2><Link href="/study-plan">Study Plan</Link></header>
        <p className="dashboard-section-note">Next five pending tasks, earliest due first</p>
        {data.upcoming_tasks.length === 0 ? <div className="dashboard-empty"><p>No pending tasks.</p><span>Create or manage your tasks in Study Plan.</span></div> :
          <ul className="dashboard-task-list">{data.upcoming_tasks.map((task) => <li className="dashboard-task" key={task.id}>
            <div className="dashboard-item-copy"><h3>{task.title}</h3><p>{task.subject_code ?? "General study"}{task.topic_title && ` · ${task.topic_title}`}{task.estimated_minutes && ` · ${task.estimated_minutes} min planned`}</p></div>
            <div className="dashboard-task-due">{task.due_at ? <>
              <time dateTime={task.due_at}>{new Intl.DateTimeFormat("en", { timeZone: data.timezone, year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(new Date(task.due_at))}</time>
              {new Date(task.due_at) < new Date(data.generated_at) && <span className="dashboard-overdue">Overdue</span>}
            </> : <span>No due date</span>}</div>
          </li>)}</ul>}
      </section>

      <section className="dashboard-section dashboard-videos" aria-labelledby="dashboard-videos">
        <header className="dashboard-section-heading"><h2 id="dashboard-videos">Video progress</h2>{videoPath && <Link href={videoPath}>Videos</Link>}</header>
        <dl className="dashboard-video-counts">
          <div><dt>Videos completed</dt><dd>{summary!.completed_videos}</dd></div>
          <div><dt>Total videos</dt><dd>{summary!.total_videos}</dd></div>
          <div><dt>Remaining</dt><dd>{summary!.remaining_videos}</dd></div>
        </dl>
        <dl className="dashboard-video-time">
          <div><dt>Completed lecture time</dt><dd>{formatDuration(summary!.completed_duration_seconds)}</dd></div>
          <div><dt>Remaining lecture time</dt><dd>{formatDuration(summary!.remaining_duration_seconds)}</dd></div>
        </dl>
        <p className="dashboard-section-note">Lecture durations, not measured study time. Times use h:mm:ss or m:ss.</p>
        {summary!.unknown_duration_videos > 0 && <p className="dashboard-section-note">{summary!.unknown_duration_videos} {summary!.unknown_duration_videos === 1 ? "video without a duration is" : "videos without a duration are"} excluded from time totals.</p>}
        {summary!.total_videos === 0 && <p className="dashboard-section-note">No lectures are available yet. Browse Subjects to view the curriculum.</p>}
      </section>

      <section className="dashboard-section dashboard-subjects" aria-labelledby="dashboard-subjects">
        <header className="dashboard-section-heading"><h2 id="dashboard-subjects">Subjects</h2><Link href="/subjects">All subjects</Link></header>
        {data.subjects.length === 0 ? <div className="dashboard-empty"><p>No active subjects available.</p></div> :
          <ul className="dashboard-subject-list">{data.subjects.map((subject) => <li className="dashboard-subject" key={subject.id}>
            <span className="subject-marker" data-color={subject.color_key ?? undefined} aria-hidden="true" />
            <div className="dashboard-subject-copy"><Link href={`/subjects/${encodeURIComponent(subject.id)}`}><strong>{subject.code}</strong><span>{subject.name}</span></Link></div>
            <div className="dashboard-subject-counts"><span>{subject.topic_count} {subject.topic_count === 1 ? "topic" : "topics"}</span><span>{subject.completed_video_count} / {subject.video_count} videos completed</span></div>
            <Link className="dashboard-subject-video" href={`/subjects/${encodeURIComponent(subject.id)}/videos`} aria-label={`Browse ${subject.code} videos`}>Videos</Link>
          </li>)}</ul>}
      </section>
    </div>}
  </>;
}
