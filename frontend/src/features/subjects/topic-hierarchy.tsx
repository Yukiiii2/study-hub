import type { CSSProperties } from "react";
import type { Topic } from "@/services/subjects";
import { flattenTopics } from "./hierarchy";

export function TopicHierarchy({ topics }: { topics: Topic[] }) {
  return <ul className="topic-list" aria-label="Topic hierarchy">
    {flattenTopics(topics).map(({ topic, depth }) => <li key={topic.id} className="topic-row" style={{ "--topic-depth": Math.min(depth, 6) } as CSSProperties}>
      <span className="sr-only">{depth === 0 ? "Top-level topic. " : `Subtopic, level ${depth + 1}. `}</span>
      <div className="topic-title">{topic.code && <span className="topic-code">{topic.code}</span>}<h3>{topic.title}</h3></div>
      {topic.description && <p>{topic.description}</p>}
    </li>)}
  </ul>;
}
