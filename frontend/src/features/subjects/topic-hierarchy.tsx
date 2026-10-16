import type { CSSProperties } from "react";
import Link from "next/link";
import type { Topic } from "@/services/subjects";
import { flattenTopics } from "./hierarchy";

function TopicActions({ topic }: { topic: Topic }) { return <div className="topic-actions">
      <Link className="topic-focus-link" href={`/focus?${new URLSearchParams({ subject_id: topic.subject_id, topic_id: topic.id })}`} aria-label={`Start focus session for ${topic.title}`}>Focus on this topic</Link>
      <Link className="topic-focus-link assistant-topic-link" href={`/assistant?${new URLSearchParams({ subject_id: topic.subject_id, topic_id: topic.id, mode: "ask", prompt: "Summarize the key concepts for this topic." })}`} aria-label={`Summarize ${topic.title} with AI`}>Summarize with AI</Link>
      <Link className="topic-focus-link assistant-topic-link" href={`/assistant?${new URLSearchParams({ subject_id: topic.subject_id, topic_id: topic.id, mode: "quiz" })}`} aria-label={`Generate question drafts for ${topic.title}`}>Generate question drafts</Link>
      </div>; }
export function TopicHierarchy({ topics, compact = false }: { topics: Topic[]; compact?: boolean }) {
  if (compact) return <ul className="mobile-topic-list" aria-label="Topic hierarchy">{flattenTopics(topics).map(({ topic, depth }) => <li key={topic.id} style={{ "--topic-depth": Math.min(depth,6) } as CSSProperties}><details><summary><span>{topic.code && <span className="topic-code">{topic.code}</span>}<strong>{topic.title}</strong></span></summary>{depth > 0 && <p className="resource-note">Subtopic, level {depth + 1}</p>}{topic.description && <p>{topic.description}</p>}<TopicActions topic={topic} /></details></li>)}</ul>;
  return <ul className="topic-list" aria-label="Topic hierarchy">
    {flattenTopics(topics).map(({ topic, depth }) => <li key={topic.id} className="topic-row" data-depth={depth === 0 ? "root" : "child"} style={{ "--topic-depth": Math.min(depth, 6) } as CSSProperties}>
      <span className="sr-only">{depth === 0 ? "Top-level topic. " : `Subtopic, level ${depth + 1}. `}</span>
      <div className="topic-copy">
      <div className="topic-title">{topic.code && <span className="topic-code">{topic.code}</span>}<h3>{topic.title}</h3></div>
      {topic.description && <p>{topic.description}</p>}
      </div>
      <TopicActions topic={topic} />
    </li>)}
  </ul>;
}
