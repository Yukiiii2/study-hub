from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.flashcards import CardCreate
from app.schemas.quizzes import QuestionInput, QuestionOption, clean_text


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class ContextInput(StrictInput):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    resource_id: UUID | None = None


class PromptInput(ContextInput):
    prompt: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("prompt")
    @classmethod
    def valid_prompt(cls, value):
        if value is None:
            return value
        clean_text(value)
        value = value.strip()
        if not value:
            raise ValueError("Prompt must be nonblank.")
        return value


class AskInput(PromptInput):
    prompt: str = Field(min_length=1, max_length=2000)


class GenerateQuizInput(PromptInput):
    count: int = Field(default=3, strict=True, ge=1, le=5)
    difficulty: Literal["basic", "intermediate", "advanced"] = "intermediate"


class GenerateCardsInput(PromptInput):
    count: int = Field(default=5, strict=True, ge=1, le=10)
    attempt_id: UUID | None = None
    question_id: UUID | None = None

    @model_validator(mode="after")
    def valid_snapshot(self):
        if (self.attempt_id is None) != (self.question_id is None):
            raise ValueError("Attempt and question are required together.")
        if self.attempt_id and any((self.subject_id, self.topic_id, self.resource_id)):
            raise ValueError("Quiz snapshot context cannot be combined with other context.")
        return self


class ExplainInput(StrictInput):
    attempt_id: UUID
    question_id: UUID


class ResolvedContext(BaseModel):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    resource_id: UUID | None = None


class Citation(BaseModel):
    resource_id: UUID
    resource_title: str
    page_number: int
    quote: str


class ResponseMetadata(BaseModel):
    provider: str | None
    model: str | None
    generated_at: datetime
    context: ResolvedContext
    grounding: Literal["resource", "topic_context", "quiz_snapshot", "none"]
    insufficient_context: bool
    notice: str | None
    citations: list[Citation]


class AnswerResponse(ResponseMetadata):
    answer: str


class QuestionDraft(QuestionInput):
    question_type: Literal["single_select", "true_false"]
    ai_draft_receipt: str = Field(min_length=1, max_length=2048, strict=True, exclude=False)


class CardDraft(CardCreate):
    status: Literal["suspended"] = "suspended"
    ai_draft_receipt: str = Field(min_length=1, max_length=2048, strict=True, exclude=False)


class QuizDraftResponse(ResponseMetadata):
    questions: list[QuestionDraft]


class CardsDraftResponse(ResponseMetadata):
    cards: list[CardDraft]


# Provider output contains no owner, curriculum IDs, scores or scheduling fields.
# The backend resolves references and applies the existing authoring validators.
class RawCitation(StrictInput):
    chunk_id: UUID
    quote: str = Field(min_length=10, max_length=400)


class RawAnswer(StrictInput):
    answer: str = Field(min_length=1, max_length=12000)
    insufficient_context: bool = False
    citations: list[RawCitation] = Field(default_factory=list, max_length=6)


class RawQuestion(StrictInput):
    question_type: Literal["single_select", "true_false"]
    prompt: str = Field(min_length=1, max_length=5000)
    explanation: str | None = Field(default=None, max_length=5000)
    options: list[QuestionOption] = Field(min_length=2, max_length=6)
    correct_keys: list[str] = Field(min_length=1, max_length=1)
    citations: list[RawCitation] = Field(default_factory=list, max_length=6)


class RawQuiz(StrictInput):
    questions: list[RawQuestion] = Field(max_length=5)
    insufficient_context: bool = False


class RawCard(StrictInput):
    front: str = Field(min_length=1, max_length=5000)
    back: str = Field(min_length=1, max_length=12000)
    notes: str | None = Field(default=None, max_length=5000)
    citations: list[RawCitation] = Field(default_factory=list, max_length=6)


class RawCards(StrictInput):
    cards: list[RawCard] = Field(max_length=10)
    insufficient_context: bool = False
