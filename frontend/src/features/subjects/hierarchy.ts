import type { Topic } from "@/services/subjects";

export type TopicRow = { topic: Topic; depth: number };

export function flattenTopics(topics: Topic[]): TopicRow[] {
  const ordered = [...topics].sort((a, b) => a.display_order - b.display_order || a.title.localeCompare(b.title) || a.id.localeCompare(b.id));
  const ids = new Set(ordered.map((topic) => topic.id));
  const children = new Map<string, Topic[]>();
  const roots: Topic[] = [];
  for (const topic of ordered) {
    if (!topic.parent_topic_id || !ids.has(topic.parent_topic_id)) roots.push(topic);
    else {
      const siblings = children.get(topic.parent_topic_id) ?? [];
      siblings.push(topic);
      children.set(topic.parent_topic_id, siblings);
    }
  }
  const result: TopicRow[] = [];
  const visited = new Set<string>();
  function walk(start: Topic) {
    const stack: TopicRow[] = [{ topic: start, depth: 0 }];
    while (stack.length) {
      const row = stack.pop()!;
      if (visited.has(row.topic.id)) continue;
      visited.add(row.topic.id);
      result.push(row);
      const descendants = children.get(row.topic.id) ?? [];
      for (let i = descendants.length - 1; i >= 0; i--) stack.push({ topic: descendants[i], depth: row.depth + 1 });
    }
  }
  for (const root of roots) walk(root);
  // Malformed cycles have no root; still show every record once without recursion.
  for (const topic of ordered) if (!visited.has(topic.id)) walk(topic);
  return result;
}
