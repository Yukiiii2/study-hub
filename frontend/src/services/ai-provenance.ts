export type AIProvenance = {
  provider: string;
  model: string;
  generated_at: string;
  subject_id?: string | null;
  topic_id?: string | null;
  resource_id?: string | null;
  source_pages?: number[];
  attempt_id?: string | null;
  question_id?: string | null;
};
