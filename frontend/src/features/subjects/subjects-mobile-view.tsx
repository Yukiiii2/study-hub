import Link from "next/link";
import type { SubjectDirectoryProps } from "./subjects-desktop-view";
import { InterfaceIcon } from "@/components/interface-icon";

export function SubjectsMobileView({ subjects, progress }: SubjectDirectoryProps) {
  return <ul className="mobile-subject-list" aria-label="Subjects">{subjects.map(subject => {
    const counts = progress?.find(item => item.id === subject.id);
    return <li data-subject={subject.code} key={subject.id}><Link className="mobile-subject-row" href={`/subjects/${subject.id}`}>
      <span className="mobile-subject-code"><span className="subject-marker" data-color={subject.color_key ?? undefined} aria-hidden="true" />{subject.code}</span><InterfaceIcon name="next" />
      <span className="mobile-subject-name">{subject.name}</span>
      {counts ? <><span className="mobile-subject-count">{counts.completed_video_count} / {counts.video_count} lectures</span>{counts.video_count > 0 && <progress value={counts.completed_video_count} max={counts.video_count} aria-label={`${subject.code} lectures completed`} />}<span className="mobile-subject-topics">{counts.topic_count} topics</span></> : <span className="resource-note">Open curriculum and lecture progress</span>}
    </Link></li>;
  })}</ul>;
}
