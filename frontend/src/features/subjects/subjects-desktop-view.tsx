import Link from "next/link";
import type { Subject } from "@/services/subjects";
import type { DashboardData } from "@/services/dashboard";
import { ProgressMeter } from "@/components/study-ui";
import { InterfaceIcon } from "@/components/interface-icon";
export type SubjectDirectoryProps = { subjects: Subject[]; progress: DashboardData["subjects"] | null };
export function SubjectsDesktopView({ subjects, progress }: SubjectDirectoryProps) { return <ul className="subject-list" aria-label="Subjects">{subjects.map((subject) => <li key={subject.id} data-subject={subject.code}>
        <Link href={`/subjects/${subject.id}`} className="subject-row">
          <span className="subject-marker" data-color={subject.color_key ?? undefined} aria-hidden="true" />
          <span className="subject-code">{subject.code}</span>
          <span className="subject-name">{subject.name}</span>
          <div className="subject-list-progress">{progress?.find(item => item.id === subject.id) ? <><ProgressMeter label="Lectures completed" value={progress.find(item => item.id === subject.id)!.completed_video_count} total={progress.find(item => item.id === subject.id)!.video_count} /><span>{progress.find(item => item.id === subject.id)!.topic_count} topics</span></> : <span>Open curriculum and lecture progress</span>}</div>
          <span className="subject-open"><InterfaceIcon name="next" /></span>
        </Link>
      </li>)}</ul>; }
