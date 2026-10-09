from datetime import datetime
from typing import Literal
from uuid import UUID
from unicodedata import category

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

QuestionType = Literal["single_select", "multi_select", "true_false"]


def clean_text(value, *, multiline=True):
    if value is not None and any(category(char) == "Cc" and (not multiline or char not in "\r\n\t") for char in value):
        raise ValueError("Text contains unsupported control characters.")
    return value


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class QuestionOption(Input):
    key: str = Field(min_length=1, max_length=5)
    text: str = Field(min_length=1, max_length=1000)

    @field_validator("text")
    @classmethod
    def nonblank(cls, value):
        clean_text(value)
        value = value.strip()
        if not value:
            raise ValueError("Option text must be nonblank.")
        return value


class QuestionInput(Input):
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    resource_id: UUID | None = None
    source_page: int | None = Field(default=None, ge=1, le=200)
    question_type: QuestionType
    prompt: str = Field(min_length=1, max_length=5000)
    explanation: str | None = Field(default=None, max_length=5000)
    options: list[QuestionOption] = Field(min_length=2, max_length=6)
    correct_keys: list[str] = Field(min_length=1, max_length=6)

    @field_validator("prompt")
    @classmethod
    def nonblank(cls, value):
        clean_text(value)
        value = value.strip()
        if not value:
            raise ValueError("Question must be nonblank.")
        return value

    @field_validator("explanation")
    @classmethod
    def valid_explanation(cls, value):
        return clean_text(value)

    @model_validator(mode="after")
    def valid_question(self):
        if self.topic_id is not None and self.subject_id is None:
            raise ValueError("Topic requires a subject.")
        if self.source_page is not None and self.resource_id is None:
            raise ValueError("Source page requires a resource.")
        keys = [o.key for o in self.options]
        if len({o.text.casefold() for o in self.options}) != len(self.options):
            raise ValueError("Option texts must be distinct.")
        allowed = {"TRUE", "FALSE"} if self.question_type == "true_false" else set("ABCDEF")
        if len(set(keys)) != len(keys) or not set(keys) <= allowed:
            raise ValueError("Options require unique valid keys.")
        if self.question_type == "true_false" and set(keys) != allowed:
            raise ValueError("True/false requires TRUE and FALSE options.")
        if len(set(self.correct_keys)) != len(self.correct_keys) or not set(self.correct_keys) <= set(keys):
            raise ValueError("Correct keys must uniquely match options.")
        if self.question_type != "multi_select" and len(self.correct_keys) != 1:
            raise ValueError("This question requires exactly one correct key.")
        return self


class QuestionResponse(QuestionInput):
    id: UUID
    origin: Literal["manual", "csv"]
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class QuestionList(BaseModel):
    questions: list[QuestionResponse]
    total: int


class ArchiveInput(Input):
    is_archived: Literal[True]


class QuizInput(Input):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    subject_id: UUID | None = None
    topic_id: UUID | None = None
    question_ids: list[UUID] = Field(min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def nonblank(cls, value):
        clean_text(value, multiline=False)
        value = value.strip()
        if not value:
            raise ValueError("Title must be nonblank.")
        return value

    @field_validator("description")
    @classmethod
    def valid_description(cls, value):
        return clean_text(value)

    @model_validator(mode="after")
    def valid_quiz(self):
        if len(set(self.question_ids)) != len(self.question_ids):
            raise ValueError("Questions must be unique.")
        if self.topic_id is not None and self.subject_id is None:
            raise ValueError("Topic requires a subject.")
        return self


class PublicQuestion(BaseModel):
    id: UUID
    question_type: QuestionType
    prompt: str
    options: list[QuestionOption]
    subject_id: UUID | None
    topic_id: UUID | None
    resource_id: UUID | None
    source_page: int | None


class TakingQuestion(PublicQuestion):
    selected_keys: list[str] = Field(default_factory=list)


class ReviewQuestion(TakingQuestion):
    correct_keys: list[str]
    explanation: str | None
    is_correct: bool


class QuizResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    subject_id: UUID | None
    topic_id: UUID | None
    is_archived: bool
    question_count: int
    active_attempt_id: UUID | None
    created_at: datetime
    updated_at: datetime


class QuizDetail(QuizResponse):
    questions: list[PublicQuestion]


class QuizList(BaseModel):
    quizzes: list[QuizResponse]
    total: int


class AnswerInput(Input):
    question_id: UUID
    selected_keys: list[str] = Field(max_length=6)


class AttemptSummary(BaseModel):
    id: UUID
    quiz_id: UUID
    title: str
    status: Literal["in_progress", "completed"]
    started_at: datetime
    completed_at: datetime | None
    score_value: int | None
    total_questions: int
    score_percent: float | None


class AttemptResponse(AttemptSummary):
    questions: list[ReviewQuestion | TakingQuestion]


class AttemptList(BaseModel):
    attempts: list[AttemptSummary]
    total: int
