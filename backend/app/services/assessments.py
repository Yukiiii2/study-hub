"""Owner-scoped assessment authoring, manual results and read-only readiness."""
from datetime import datetime, time, timezone
from decimal import Decimal, ROUND_HALF_UP, localcontext
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import ValidationError

from app.repositories import assessments as repo
from app.schemas.assessments import (AssessmentCreate, AssessmentDetail, AssessmentList,
                                    AssessmentResponse, AttemptCreate, AttemptList, AttemptResponse)


class AssessmentError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _now():
    return datetime.now(timezone.utc)


def percentage(numerator, denominator):
    if numerator is None or denominator is None or not denominator:
        return None
    with localcontext() as context:
        context.prec = 40
        return (Decimal(numerator) * 100 / Decimal(denominator)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _required(row, kind="Assessment"):
    if row is None:
        raise AssessmentError(404, f"{kind} not found.")
    return row


def _response(schema, row):
    return schema.model_validate(row).model_dump()


def _merged(schema, current, patch):
    values = {key: current[key] for key in schema.model_fields}
    values.update(patch.model_dump(exclude_unset=True))
    try:
        return schema.model_validate(values)
    except ValidationError:
        raise AssessmentError(422, "Invalid assessment fields or result.") from None


def _coverage(connection, data):
    if not repo.valid_coverage(connection, data.topic_ids, data.subject_ids):
        raise AssessmentError(422, "Choose active curriculum coverage without topic and whole-subject overlap.")


def _editable(row):
    if row["status"] == "archived":
        raise AssessmentError(409, "Archived assessments cannot accept result changes.")


def list_assessments(user_id, **filters):
    with repo.transaction(readonly=True) as connection:
        return _response(AssessmentList, repo.list_assessments(connection, user_id, **filters))


def get_assessment(user_id, assessment_id):
    with repo.transaction(readonly=True) as connection:
        row = _required(repo.get_assessment(connection, user_id, assessment_id))
        timezone_name = repo.profile_timezone(connection, user_id)
        try:
            zone = ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError, TypeError):
            raise AssessmentError(503, "Assessment timezone is unavailable. Try again.") from None
        now = _now()
        day_start = datetime.combine(now.astimezone(zone).date(), time.min, tzinfo=zone).astimezone(timezone.utc)
        counts = repo.readiness_counts(connection, user_id, assessment_id, now, day_start)
        readiness = {**counts, "as_of": now, "timezone": timezone_name,
                     "video_completion_percentage": percentage(counts["completed_videos"], counts["total_videos"]),
                     "quiz_accuracy_percentage": percentage(counts["quiz_correct_answers"], counts["quiz_graded_answers"])}
        return _response(AssessmentDetail, {**row, "readiness": readiness})


def create_assessment(user_id, data):
    with repo.transaction() as connection:
        _coverage(connection, data)
        return _response(AssessmentResponse, repo.write_assessment(connection, user_id, data))


def patch_assessment(user_id, assessment_id, patch):
    with repo.transaction() as connection:
        current = _required(repo.get_assessment(connection, user_id, assessment_id, lock=True))
        data = _merged(AssessmentCreate, current, patch)
        _coverage(connection, data)
        return _response(AssessmentResponse, repo.write_assessment(connection, user_id, data, assessment_id))


def delete_assessment(user_id, assessment_id):
    with repo.transaction() as connection:
        _required(repo.get_assessment(connection, user_id, assessment_id, lock=True))
        repo.archive_assessment(connection, user_id, assessment_id)


def _attempt_values(data):
    return {**data.model_dump(), "percentage": percentage(data.score, data.max_score)}


def create_attempt(user_id, assessment_id, data):
    with repo.transaction() as connection:
        _editable(_required(repo.get_assessment(connection, user_id, assessment_id, lock=True)))
        return _response(AttemptResponse, repo.write_attempt(connection, user_id, assessment_id, _attempt_values(data)))


def patch_attempt(user_id, attempt_id, patch):
    with repo.transaction() as connection:
        before = _required(repo.get_attempt(connection, user_id, attempt_id), "Attempt")
        # Definition lock precedes attempt lock, serializing changes with archival.
        _editable(_required(repo.get_assessment(connection, user_id, before["assessment_id"], lock=True)))
        current = _required(repo.get_attempt(connection, user_id, attempt_id, lock=True), "Attempt")
        data = _merged(AttemptCreate, current, patch)
        return _response(AttemptResponse, repo.write_attempt(connection, user_id, current["assessment_id"], _attempt_values(data), attempt_id))


def list_attempts(user_id, assessment_id, **filters):
    with repo.transaction(readonly=True) as connection:
        _required(repo.get_assessment(connection, user_id, assessment_id))
        return _response(AttemptList, repo.list_attempts(connection, user_id, assessment_id, **filters))
