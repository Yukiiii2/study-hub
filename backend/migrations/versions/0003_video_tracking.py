"""Shared lectures and isolated per-user tracking."""
from alembic import op

revision = "0003_video_tracking"
down_revision = "0002_seed_subjects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.videos (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            topic_id uuid NOT NULL REFERENCES public.topics(id),
            title text NOT NULL CHECK (btrim(title) <> ''),
            duration_seconds integer CHECK (duration_seconds >= 0),
            source_url text,
            source_code text CHECK (source_code IS NULL OR btrim(source_code) <> ''),
            display_order integer NOT NULL DEFAULT 0 CHECK (display_order >= 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (topic_id, source_code)
        );
        CREATE INDEX videos_topic_order_idx ON public.videos(topic_id, display_order);
        CREATE TABLE public.user_video_progress (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            video_id uuid NOT NULL REFERENCES public.videos(id),
            status text NOT NULL DEFAULT 'not_started'
                CHECK (status IN ('not_started', 'in_progress', 'completed')),
            watched_seconds integer CHECK (watched_seconds >= 0),
            started_at timestamptz,
            completed_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (user_id, video_id),
            CHECK ((status = 'completed') = (completed_at IS NOT NULL))
        );
        CREATE INDEX user_video_progress_video_idx ON public.user_video_progress(video_id);
        CREATE TRIGGER videos_updated_at BEFORE UPDATE ON public.videos
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE TRIGGER user_video_progress_updated_at BEFORE UPDATE ON public.user_video_progress
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.user_video_progress ENABLE ROW LEVEL SECURITY;
        REVOKE ALL ON public.videos, public.user_video_progress FROM PUBLIC, anon, authenticated;
        GRANT SELECT ON public.videos, public.user_video_progress TO authenticated;
        -- Mutations use FastAPI. Privileged backend queries must always scope progress by verified user UUID.
        CREATE POLICY videos_read_authenticated ON public.videos FOR SELECT TO authenticated
            USING (EXISTS (SELECT 1 FROM public.topics t JOIN public.subjects s ON s.id = t.subject_id
                          WHERE t.id = topic_id AND s.is_active));
        CREATE POLICY video_progress_read_own ON public.user_video_progress FOR SELECT TO authenticated
            USING ((SELECT auth.uid()) = user_id);
        -- No browser/anon progress write grants or policies: the API owns timestamp/status semantics.
    """)


def downgrade() -> None:
    raise RuntimeError("Dropping video/progress data is destructive and requires explicit approval.")
