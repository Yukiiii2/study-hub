"""Owner-scoped plans, recurrence snapshots, tasks and actual sessions."""
from alembic import op

revision = "0004_study_planner"
down_revision = "0003_video_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.study_events (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            title text NOT NULL CHECK (btrim(title) <> ''),
            event_type text NOT NULL DEFAULT 'general'
                CHECK (event_type IN ('lecture','reading','drill','recall','quiz','assessment','general')),
            start_at timestamptz NOT NULL,
            end_at timestamptz NOT NULL,
            timezone text NOT NULL CHECK (btrim(timezone) <> ''),
            status text NOT NULL DEFAULT 'scheduled'
                CHECK (status IN ('scheduled','completed','skipped','cancelled')),
            recurrence_rule text CHECK (recurrence_rule IS NULL OR btrim(recurrence_rule) <> ''),
            notes text,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (id, user_id),
            FOREIGN KEY (topic_id, subject_id) REFERENCES public.topics(id, subject_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK (start_at < end_at),
            CHECK (recurrence_rule IS NULL OR status = 'scheduled')
        );
        CREATE INDEX study_events_owner_range_idx ON public.study_events(user_id, start_at, end_at);

        CREATE TABLE public.study_event_occurrences (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            study_event_id uuid NOT NULL,
            occurrence_date date NOT NULL,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            title text NOT NULL CHECK (btrim(title) <> ''),
            event_type text NOT NULL
                CHECK (event_type IN ('lecture','reading','drill','recall','quiz','assessment','general')),
            start_at timestamptz NOT NULL,
            end_at timestamptz NOT NULL,
            status text NOT NULL DEFAULT 'scheduled'
                CHECK (status IN ('scheduled','completed','skipped','cancelled')),
            notes text,
            is_deleted boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (id, user_id),
            UNIQUE (id, study_event_id, user_id),
            UNIQUE (study_event_id, occurrence_date),
            FOREIGN KEY (study_event_id, user_id) REFERENCES public.study_events(id, user_id) ON DELETE CASCADE,
            FOREIGN KEY (topic_id, subject_id) REFERENCES public.topics(id, subject_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK (start_at < end_at)
        );
        CREATE INDEX study_occurrences_owner_range_idx ON public.study_event_occurrences(user_id, start_at, end_at);

        CREATE TABLE public.study_tasks (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            title text NOT NULL CHECK (btrim(title) <> ''),
            task_type text NOT NULL DEFAULT 'general'
                CHECK (task_type IN ('lecture','reading','drill','recall','quiz','assessment','general')),
            estimated_minutes integer CHECK (estimated_minutes > 0),
            due_at timestamptz,
            status text NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','scheduled','completed','cancelled')),
            scheduled_event_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            FOREIGN KEY (scheduled_event_id, user_id) REFERENCES public.study_events(id, user_id)
                ON DELETE SET NULL (scheduled_event_id),
            FOREIGN KEY (topic_id, subject_id) REFERENCES public.topics(id, subject_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK (status <> 'scheduled' OR scheduled_event_id IS NOT NULL)
        );
        CREATE INDEX study_tasks_owner_status_idx ON public.study_tasks(user_id, status, due_at);
        CREATE INDEX study_tasks_event_idx ON public.study_tasks(scheduled_event_id);

        CREATE TABLE public.study_sessions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            study_event_id uuid,
            occurrence_id uuid,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            started_at timestamptz NOT NULL DEFAULT now(),
            ended_at timestamptz,
            duration_seconds integer CHECK (duration_seconds >= 0),
            notes text,
            created_at timestamptz NOT NULL DEFAULT now(),
            FOREIGN KEY (study_event_id, user_id) REFERENCES public.study_events(id, user_id)
                ON DELETE SET NULL (study_event_id),
            FOREIGN KEY (occurrence_id, user_id) REFERENCES public.study_event_occurrences(id, user_id)
                ON DELETE SET NULL (occurrence_id),
            FOREIGN KEY (occurrence_id, study_event_id, user_id)
                REFERENCES public.study_event_occurrences(id, study_event_id, user_id)
                ON DELETE SET NULL (occurrence_id),
            FOREIGN KEY (topic_id, subject_id) REFERENCES public.topics(id, subject_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK ((ended_at IS NULL) = (duration_seconds IS NULL)),
            CHECK (ended_at IS NULL OR (ended_at >= started_at
                AND duration_seconds = floor(extract(epoch FROM ended_at - started_at))::integer))
        );
        CREATE UNIQUE INDEX study_sessions_one_active_idx ON public.study_sessions(user_id) WHERE ended_at IS NULL;
        CREATE INDEX study_sessions_owner_start_idx ON public.study_sessions(user_id, started_at);
        CREATE INDEX study_sessions_event_idx ON public.study_sessions(study_event_id);
        CREATE INDEX study_sessions_occurrence_idx ON public.study_sessions(occurrence_id);

        -- Unlink tasks before FK actions, updating status and link together.
        CREATE FUNCTION public.study_hub_unschedule_tasks()
        RETURNS trigger LANGUAGE plpgsql SET search_path = '' AS $$
        BEGIN
            UPDATE public.study_tasks SET scheduled_event_id = NULL,
                status = CASE WHEN status = 'scheduled' THEN 'pending' ELSE status END
            WHERE scheduled_event_id = OLD.id AND user_id = OLD.user_id;
            RETURN OLD;
        END;
        $$;
        REVOKE ALL ON FUNCTION public.study_hub_unschedule_tasks() FROM PUBLIC, anon, authenticated;
        CREATE TRIGGER study_events_unschedule_tasks BEFORE DELETE ON public.study_events
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_unschedule_tasks();
    """)
    for table in ("study_events", "study_event_occurrences", "study_tasks", "study_sessions"):
        # Identifiers are a fixed migration list, never request input.
        if table != "study_sessions":
            op.execute(f"CREATE TRIGGER {table}_updated_at BEFORE UPDATE ON public.{table} "
                       "FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at()")
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC, anon, authenticated")
        op.execute(f"GRANT SELECT ON public.{table} TO authenticated")
        op.execute(f"CREATE POLICY {table}_read_own ON public.{table} FOR SELECT TO authenticated "
                   "USING ((SELECT auth.uid()) = user_id)")
    # Browser mutation grants are deliberately absent: FastAPI validates references and timestamps.


def downgrade() -> None:
    raise RuntimeError("Dropping planner/activity data is destructive and requires explicit approval.")
