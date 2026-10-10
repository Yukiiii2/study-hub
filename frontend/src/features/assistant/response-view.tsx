import Link from "next/link";
import type { AIResponse, AIAnswer } from "@/services/ai";

export function AIResponseView({ response }: { response: AIResponse & Partial<Pick<AIAnswer, "answer">> }) {
  return <section className="assistant-response" aria-label="AI response">
    <p className="resource-note">{response.provider && response.model ? `Generated with ${response.provider} / ${response.model}. ` : ""}{response.generated_at && <>Generated <time dateTime={response.generated_at}>{new Date(response.generated_at).toLocaleString()}</time>. </>}Verify study content before using it.</p>
    {response.notice && <p className="planner-notice" role="status">{response.notice}</p>}
    {response.grounding === "topic_context" && <p className="resource-note">AI knowledge using curriculum context. No uploaded source supports this response.</p>}
    {response.grounding === "quiz_snapshot" && <p className="resource-note">Based on the saved completed quiz answer. Any explanation beyond cited source text is AI assistance.</p>}
    {response.insufficient_context && <p className="resource-note">There is not enough relevant context. Choose a ready text PDF or refine the subject, topic and prompt.</p>}
    {response.answer && <p className="assistant-answer">{response.answer}</p>}
    {!!response.citations.length && <div className="assistant-citations"><h3>Source quotes</h3><p className="resource-note">Quotes point to supporting text; check the original PDF to verify the explanation.</p>{response.citations.map((citation, index) => <figure key={`${citation.resource_id}:${citation.page_number}:${index}`}><blockquote>{citation.quote}</blockquote><figcaption><Link className="quiz-text-link" href={`/library/${encodeURIComponent(citation.resource_id)}`}>{citation.resource_title} · Page {citation.page_number}</Link></figcaption></figure>)}</div>}
  </section>;
}
