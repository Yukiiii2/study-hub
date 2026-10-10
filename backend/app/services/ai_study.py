"""Validated transient study drafts; this service never writes application data."""
import asyncio
import json
from datetime import datetime, timezone
from uuid import UUID

from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app.ai.draft_receipts import mint_draft_receipt, DraftReceiptError
from app.ai.errors import AIError
from app.ai.limits import limiter
from app.ai.prompts import SYSTEM, build_material
from app.ai.retrieval import query_terms, summary_request
from app.repositories import ai_context as repo
from app.schemas.ai import (RawAnswer, RawCards, RawQuiz, QuestionDraft, CardDraft)
from app.schemas.flashcards import CardCreate
from app.schemas.quizzes import QuestionInput

INSUFFICIENT = "The selected context does not contain enough information. Choose a text PDF, subject or topic, or a more relevant question."
TOPIC_NOTICE = "AI knowledge with curriculum context. Verify against your study materials; no uploaded source supports this response."
SNAPSHOT_NOTICE = "AI explanation based on your submitted quiz snapshot. Your recorded answer and grade are unchanged."
RESOURCE_NOTICE = "AI response based on selected PDF passages. It may not cover the whole document; verify the cited source."


def _empty_context():
    return {"subject_id": None, "topic_id": None, "resource_id": None}


def _resolve_context(user_id, data, action):
    context = _empty_context()
    result = {"context": context, "grounding": "none", "curriculum": {}, "passages": [],
              "snapshot": None, "resource": None, "notice": None}
    attempt_id = getattr(data, "attempt_id", None)
    subject_id = getattr(data, "subject_id", None)
    topic_id = getattr(data, "topic_id", None)
    resource_id = getattr(data, "resource_id", None)
    if not any((attempt_id, subject_id, topic_id, resource_id)):
        return result
    with repo.read_context() as connection:
        if attempt_id:
            attempt = repo.get_attempt(connection, user_id, attempt_id)
            if attempt is None:
                raise AIError(404, "Quiz attempt not found.")
            if attempt["status"] != "completed":
                raise AIError(409, "Submit this quiz attempt before using AI review.")
            question = next((q for q in attempt["snapshot"] if str(q["id"]) == str(data.question_id)), None)
            if question is None:
                raise AIError(404, "Question not found in this quiz attempt.")
            selections = repo.answers(connection, user_id, attempt_id).get(str(data.question_id), {})
            snapshot = {key: question.get(key) for key in
                        ("question_type", "prompt", "options", "correct_keys", "explanation")}
            snapshot.update(selected_keys=selections.get("selected_keys", []), is_correct=selections.get("is_correct", False))
            if len(json.dumps(snapshot, ensure_ascii=False)) > 11500:
                raise AIError(422, "This quiz snapshot is too large for AI review.")
            result.update(snapshot=snapshot, grounding="quiz_snapshot", notice=SNAPSHOT_NOTICE)
            subject_id = UUID(question["subject_id"]) if question.get("subject_id") else None
            topic_id = UUID(question["topic_id"]) if question.get("topic_id") else None
            resource_id = UUID(question["resource_id"]) if question.get("resource_id") else None
            # Snapshot remains usable after curriculum/resource deletion. Stale IDs
            # are never forwarded into draft save links or fabricated citations.
            curriculum = repo.curriculum(connection, subject_id, topic_id)
            if curriculum:
                context.update(subject_id=curriculum["subject"]["id"] if curriculum["subject"] else None,
                               topic_id=curriculum["topic"]["id"] if curriculum["topic"] else None)
            if resource_id:
                resource = repo.get_resource(connection, user_id, resource_id)
                if (resource and resource["resource_type"] == "pdf" and resource["processing_status"] == "ready"
                        and (not resource["subject_id"] or resource["subject_id"] == context["subject_id"])
                        and (not resource["topic_id"] or resource["topic_id"] == context["topic_id"])):
                    context["resource_id"] = resource_id
                    snapshot["resource_title"] = resource["title"][:500]
            # Source association is retained, but this response remains grounded
            # in the submitted snapshot; no PDF passages or citations are implied.
            return result

        resource = None
        if resource_id:
            resource = repo.get_resource(connection, user_id, resource_id)
            if resource is None:
                raise AIError(404, "Resource not found.")
            if resource["resource_type"] != "pdf" or resource["processing_status"] != "ready":
                raise AIError(422, "Choose an owned, ready PDF with extracted text.")
            if ((subject_id and resource["subject_id"] and subject_id != resource["subject_id"])
                    or (topic_id and resource["topic_id"] and topic_id != resource["topic_id"])):
                raise AIError(422, "Resource must match the selected subject and topic.")
            subject_id = subject_id or resource["subject_id"]
            topic_id = topic_id or resource["topic_id"]
        curriculum = repo.curriculum(connection, subject_id, topic_id)
        if curriculum is None:
            raise AIError(422, "Choose an active subject and its matching topic.")
        context.update(subject_id=curriculum["subject"]["id"] if curriculum["subject"] else None,
                       topic_id=curriculum["topic"]["id"] if curriculum["topic"] else None,
                       resource_id=resource_id)
        result["curriculum"] = curriculum
        if resource:
            prompt = getattr(data, "prompt", None)
            terms = query_terms(prompt)
            allow_first = (action != "ask" and prompt is None) or summary_request(prompt)
            selected = repo.passages(connection, user_id, resource_id, terms, allow_first=allow_first)
            total = len(json.dumps(curriculum, ensure_ascii=False, default=str)) + 1000
            bounded = []
            for row in selected[:6]:
                content = row["content"][:min(1800, 12000 - total)]
                if not content.strip():
                    continue
                total += len(content)
                bounded.append({"chunk_id": str(row["id"]), "page_number": row["page_number"], "content": content})
            result.update(grounding="resource", resource=resource, passages=bounded, notice=RESOURCE_NOTICE)
        else:
            result.update(grounding="topic_context", notice=TOPIC_NOTICE)
    return result


def _metadata(resolved, *, provider=None, model=None, insufficient=False):
    return {"provider": provider, "model": model, "generated_at": datetime.now(timezone.utc),
            "context": resolved["context"], "grounding": resolved["grounding"],
            "insufficient_context": insufficient,
            "notice": INSUFFICIENT if insufficient else resolved["notice"], "citations": []}


def _citations(raw_citations, resolved, *, required=False):
    chunks = {passage["chunk_id"]: passage for passage in resolved["passages"]}
    if required and not raw_citations:
        raise AIError(502, "AI response did not provide valid source support. Try again.")
    citations = []
    seen = set()
    for citation in raw_citations:
        chunk = chunks.get(str(citation.chunk_id))
        if chunk is None or citation.quote not in chunk["content"] or not citation.quote.strip():
            raise AIError(502, "AI response did not provide valid source support. Try again.")
        identity = (str(citation.chunk_id), citation.quote)
        if identity in seen:
            continue
        seen.add(identity)
        citations.append({"resource_id": resolved["context"]["resource_id"],
                          "resource_title": resolved["resource"]["title"],
                          "page_number": chunk["page_number"], "quote": citation.quote})
    return citations


def _receipt(user_id, kind, metadata, data, citations):
    return mint_draft_receipt(user_id, kind, provider=metadata["provider"], model=metadata["model"],
                              generated_at=metadata["generated_at"], **metadata["context"],
                              source_pages=sorted({citation["page_number"] for citation in citations}),
                              attempt_id=getattr(data, "attempt_id", None),
                              question_id=getattr(data, "question_id", None))


async def study(user_id, data, action, provider_factory):
    resolved = await run_in_threadpool(_resolve_context, user_id, data, action)
    field = "questions" if action == "generate-quiz" else "cards" if action == "generate-flashcards" else "answer"
    if resolved["grounding"] == "none" or (resolved["grounding"] == "resource" and not resolved["passages"]):
        return {**_metadata(resolved, insufficient=True), field: INSUFFICIENT if field == "answer" else []}
    schema_type = RawQuiz if field == "questions" else RawCards if field == "cards" else RawAnswer
    count = getattr(data, "count", None)
    material = build_material(action=action, prompt=getattr(data, "prompt", None), count=count,
                              difficulty=getattr(data, "difficulty", None), context=resolved,
                              curriculum=resolved["curriculum"], passages=resolved["passages"], snapshot=resolved["snapshot"])
    with limiter.acquire(user_id):
        provider = provider_factory()
        try:
            async with asyncio.timeout(30):
                output = await provider.generate(system=SYSTEM, material=material, schema=schema_type.model_json_schema())
            encoded = json.dumps(output, ensure_ascii=False)
            if len(encoded) > 24000:
                raise ValueError("Oversized output")
            parsed = schema_type.model_validate_json(encoded)
            metadata = _metadata(resolved, provider=provider.provider, model=provider.model,
                                 insufficient=parsed.insufficient_context)
            if parsed.insufficient_context:
                if (field != "answer" and getattr(parsed, field)) or (field == "answer" and parsed.citations):
                    raise ValueError("Unsupported insufficient response")
                return {**metadata, field: INSUFFICIENT if field == "answer" else []}
            required = resolved["grounding"] == "resource"
            if field == "answer":
                answer = parsed.answer.strip()
                if not answer:
                    raise ValueError("Blank answer")
                metadata["citations"] = _citations(parsed.citations, resolved, required=required)
                return {**metadata, "answer": answer}
            drafts = []
            seen = set()
            items = getattr(parsed, field)
            if len(items) != count:
                raise ValueError("Incorrect draft count")
            for item in items:
                citations = _citations(item.citations, resolved, required=required)
                values = item.model_dump(exclude={"citations"})
                values.update(**resolved["context"], source_page=citations[0]["page_number"] if citations else None)
                if field == "questions":
                    validated = QuestionInput.model_validate(values)
                    identity = " ".join(validated.prompt.casefold().split())
                    draft_type, kind = QuestionDraft, "question"
                else:
                    values["status"] = "suspended"
                    validated = CardCreate.model_validate(values)
                    identity = " ".join(validated.front.casefold().split())
                    draft_type, kind = CardDraft, "flashcard"
                if identity in seen:
                    raise ValueError("Duplicate draft")
                seen.add(identity)
                receipt = _receipt(user_id, kind, metadata, data, citations)
                drafts.append(draft_type.model_validate({**validated.model_dump(), "ai_draft_receipt": receipt}))
                for citation in citations:
                    if citation not in metadata["citations"]:
                        metadata["citations"].append(citation)
            return {**metadata, field: drafts}
        except AIError:
            raise
        except TimeoutError:
            raise AIError(503, "AI provider is unavailable. Try again.") from None
        except DraftReceiptError:
            raise AIError(503, "AI drafts cannot be prepared. Try again.") from None
        except (ValidationError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
            raise AIError(502, "AI returned an invalid response. Try again.") from None
