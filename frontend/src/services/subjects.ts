import { authenticatedGet } from "./api";

export type Subject = {
  id: string;
  code: string;
  name: string;
  display_order: number;
  color_key: string | null;
};

export type Topic = {
  id: string;
  subject_id: string;
  parent_topic_id: string | null;
  code: string | null;
  title: string;
  description: string | null;
  display_order: number;
};

export const getSubjects = (signal?: AbortSignal) => authenticatedGet<Subject[]>("/api/subjects", signal);
export const getSubject = (id: string, signal?: AbortSignal) => authenticatedGet<Subject>(`/api/subjects/${encodeURIComponent(id)}`, signal);
export const getSubjectTopics = (id: string, signal?: AbortSignal) => authenticatedGet<Topic[]>(`/api/subjects/${encodeURIComponent(id)}/topics`, signal);
export const getTopic = (id: string, signal?: AbortSignal) => authenticatedGet<Topic>(`/api/topics/${encodeURIComponent(id)}`, signal);
