"""Planner validation and transactional business rules; HTTP/auth live in the API."""
from app.repositories import planner as repo
from app.services.planner_recurrence import (
    PlannerError, expand_events, get_zone, occurrence, snapshot_response, validate_event, validate_range,
)


def required(row, name):
    if row is None:
        raise PlannerError(f"{name} not found.", 404)
    return row


def associations(connection, data):
    if not repo.valid_associations(connection, data.get("subject_id"), data.get("topic_id")):
        raise PlannerError("Select an active subject and a topic belonging to that subject.")


def event_data(connection, user_id, body):
    data = body.model_dump()
    data["timezone"] = data["timezone"] or repo.profile_timezone(connection, user_id)
    validate_event(data)
    associations(connection, data)
    return data


def get_context(user_id):
    with repo.transaction() as connection:
        name = repo.profile_timezone(connection, user_id)
        get_zone(name)
        return {"timezone": name, "active_session": repo.active_session(connection, user_id)}


def list_events(user_id, start_at, end_at):
    validate_range(start_at, end_at)
    with repo.transaction() as connection:
        events, snapshots = repo.event_range(connection, user_id, start_at, end_at)
        return expand_events(events, snapshots, start_at, end_at)


def get_event(user_id, event_id):
    with repo.transaction() as connection:
        return repo.get_record(connection, "events", user_id, event_id)


def create_event(user_id, body):
    with repo.transaction() as connection:
        return repo.insert_record(connection, "events", user_id, event_data(connection, user_id, body))


def patch_event(user_id, event_id, body):
    with repo.transaction() as connection:
        stored = required(repo.get_record(connection, "events", user_id, event_id, lock=True), "Event")
        changes = body.model_dump(exclude_unset=True)
        data = {key: value for key, value in stored.items() if key in repo.WRITABLE["events"]}
        data.update(changes)
        validate_event(data)
        associations(connection, data)
        if data["timezone"] != stored["timezone"] and repo.has_snapshots(connection, user_id, event_id):
            raise PlannerError("A series with saved occurrences cannot change timezone.", 409)
        if stored["recurrence_rule"] and not data["recurrence_rule"] and repo.has_snapshots(connection, user_id, event_id):
            raise PlannerError("A series with saved occurrences cannot become a one-off event.", 409)
        return repo.update_record(connection, "events", user_id, event_id, changes)


def delete_event(user_id, event_id):
    with repo.transaction() as connection:
        required(repo.get_record(connection, "events", user_id, event_id, lock=True), "Event")
        repo.delete_record(connection, "events", user_id, event_id)


def resolve_occurrence(connection, user_id, event, day):
    snapshot = repo.get_snapshot(connection, user_id, event["id"], day)
    if snapshot:
        if snapshot["is_deleted"]:
            raise PlannerError("Occurrence not found.", 404)
        return snapshot_response(event, snapshot), snapshot
    return occurrence(event, day), None


def save_snapshot(connection, user_id, event_id, day, data, existing=None, *, deleted=False):
    fields = ("subject_id", "topic_id", "title", "event_type", "start_at", "end_at", "status", "notes")
    values = {key: data[key] for key in fields}
    values.update(study_event_id=event_id, occurrence_date=day, is_deleted=deleted)
    if existing:
        return repo.update_record(connection, "occurrences", user_id, existing["id"], values)
    return repo.insert_record(connection, "occurrences", user_id, values)


def patch_occurrence(user_id, event_id, day, body=None, *, deleted=False):
    with repo.transaction() as connection:
        event = required(repo.get_record(connection, "events", user_id, event_id, lock=True), "Event")
        # Repeated suppression is idempotent, including saved dates removed by a series edit.
        existing = repo.get_snapshot(connection, user_id, event_id, day)
        if deleted and existing and existing["is_deleted"]:
            return None
        data, existing = resolve_occurrence(connection, user_id, event, day)
        if body:
            data.update(body.model_dump(exclude_unset=True))
        validation = {**data, "recurrence_rule": None}
        validate_event(validation)
        associations(connection, data)
        saved = save_snapshot(connection, user_id, event_id, day, data, existing, deleted=deleted)
        return snapshot_response(event, saved)


def list_tasks(user_id):
    with repo.transaction() as connection:
        return repo.list_tasks(connection, user_id)


def create_task(user_id, body):
    with repo.transaction() as connection:
        data = body.model_dump()
        associations(connection, data)
        return repo.insert_record(connection, "tasks", user_id, data)


def patch_task(user_id, task_id, body):
    with repo.transaction() as connection:
        stored = required(repo.get_record(connection, "tasks", user_id, task_id, lock=True), "Task")
        changes = body.model_dump(exclude_unset=True)
        data = {**stored, **changes}
        associations(connection, data)
        if changes.get("status") == "pending":
            changes["scheduled_event_id"] = None
        return repo.update_record(connection, "tasks", user_id, task_id, changes)


def delete_task(user_id, task_id):
    with repo.transaction() as connection:
        if not repo.delete_record(connection, "tasks", user_id, task_id):
            raise PlannerError("Task not found.", 404)


def schedule_task(user_id, task_id, body):
    with repo.transaction() as connection:
        task = required(repo.get_record(connection, "tasks", user_id, task_id, lock=True), "Task")
        if task["status"] != "pending" or task.get("scheduled_event_id"):
            raise PlannerError("Only an unscheduled pending task can be scheduled.", 409)
        if body.subject_id != task["subject_id"] or body.topic_id != task["topic_id"]:
            raise PlannerError("The scheduled event must retain the task's subject and topic.")
        if body.status != "scheduled":
            raise PlannerError("The new task event must be scheduled.")
        data = event_data(connection, user_id, body)
        event = repo.insert_record(connection, "events", user_id, data)
        repo.update_record(connection, "tasks", user_id, task_id, {"status": "scheduled", "scheduled_event_id": event["id"]})
        return event


def list_sessions(user_id, start_at=None, end_at=None):
    if start_at and end_at:
        validate_range(start_at, end_at, bounded=False)
    with repo.transaction() as connection:
        return repo.list_sessions(connection, user_id, start_at, end_at)


def create_session(user_id, body):
    with repo.transaction() as connection:
        if repo.active_session(connection, user_id):
            raise PlannerError("Stop your active session before starting another.", 409)
        data = {"study_event_id": body.study_event_id, "occurrence_id": None,
                "subject_id": body.subject_id, "topic_id": body.topic_id,
                "activity_type": body.activity_type, "notes": body.notes}
        if body.study_event_id:
            event = required(repo.get_record(connection, "events", user_id, body.study_event_id, lock=True), "Event")
            context = event
            if event["recurrence_rule"]:
                if body.occurrence_date is None:
                    raise PlannerError("A recurring session requires an occurrence date.")
                context, snapshot = resolve_occurrence(connection, user_id, event, body.occurrence_date)
                snapshot = snapshot or save_snapshot(connection, user_id, event["id"], body.occurrence_date, context)
                data["occurrence_id"] = snapshot["id"]
            elif body.occurrence_date is not None:
                raise PlannerError("A one-off event has no occurrence date.")
            for key in ("subject_id", "topic_id"):
                if key in body.model_fields_set and getattr(body, key) != context[key]:
                    raise PlannerError("Event-linked sessions inherit the event's subject and topic.")
                data[key] = context[key]
        elif body.occurrence_date is not None:
            raise PlannerError("An occurrence date requires an event.")
        associations(connection, data)
        # The database partial unique index arbitrates simultaneous starts; failed transactions
        # also roll back any newly materialized snapshot.
        return repo.insert_record(connection, "sessions", user_id, data)


def patch_session(user_id, session_id, body):
    with repo.transaction() as connection:
        required(repo.get_record(connection, "sessions", user_id, session_id, lock=True), "Session")
        changes = body.model_dump(exclude_unset=True)
        notes = {"notes": changes["notes"]} if "notes" in changes else {}
        if body.action == "stop":
            return repo.stop_session(connection, user_id, session_id, notes)
        return repo.update_record(connection, "sessions", user_id, session_id, notes)
