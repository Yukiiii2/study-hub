"""Private assessment definitions, normalized coverage and manual result history."""
from alembic import op

revision = "0008_assessments"
down_revision = "0007_flashcards"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.assessments (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            title text NOT NULL CHECK (btrim(title)<>'' AND char_length(title)<=200),
            description text CHECK (char_length(description)<=5000),
            scheduled_at timestamptz,
            status text NOT NULL DEFAULT 'planned' CHECK (status IN ('planned','completed','cancelled','archived')),
            source_key text CHECK (source_key IS NULL OR btrim(source_key)<>''),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE(id,user_id), UNIQUE(user_id,source_key)
        );
        CREATE INDEX assessments_owner_schedule_idx ON public.assessments(user_id,scheduled_at,created_at,id);
        CREATE TABLE public.assessment_topics (
            assessment_id uuid NOT NULL,
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            topic_id uuid NOT NULL REFERENCES public.topics(id),
            display_order integer NOT NULL CHECK (display_order BETWEEN 0 AND 499),
            PRIMARY KEY(assessment_id,topic_id), UNIQUE(assessment_id,display_order),
            FOREIGN KEY(assessment_id,user_id) REFERENCES public.assessments(id,user_id) ON DELETE CASCADE
        );
        CREATE TABLE public.assessment_subjects (
            assessment_id uuid NOT NULL,
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid NOT NULL REFERENCES public.subjects(id),
            display_order integer NOT NULL CHECK (display_order BETWEEN 0 AND 499),
            PRIMARY KEY(assessment_id,subject_id), UNIQUE(assessment_id,display_order),
            FOREIGN KEY(assessment_id,user_id) REFERENCES public.assessments(id,user_id) ON DELETE CASCADE
        );
        CREATE TABLE public.assessment_attempts (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            assessment_id uuid NOT NULL,
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            started_at timestamptz,
            completed_at timestamptz,
            score numeric(18,4),
            max_score numeric(18,4),
            percentage numeric(7,4),
            notes text CHECK (char_length(notes)<=5000),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE(id,user_id),
            FOREIGN KEY(assessment_id,user_id) REFERENCES public.assessments(id,user_id),
            CHECK (started_at IS NULL OR completed_at IS NULL OR completed_at>=started_at),
            CHECK ((score IS NULL AND max_score IS NULL AND percentage IS NULL) OR
                (score IS NOT NULL AND max_score IS NOT NULL AND percentage IS NOT NULL AND completed_at IS NOT NULL
                 AND score::text NOT IN ('NaN','Infinity','-Infinity') AND max_score::text NOT IN ('NaN','Infinity','-Infinity')
                 AND score>=0 AND max_score>0 AND score<=max_score AND percentage BETWEEN 0 AND 100
                 AND percentage=round(score/max_score*100,4)))
        );
        CREATE INDEX assessment_attempts_owner_assessment_idx ON public.assessment_attempts(user_id,assessment_id,created_at DESC,id DESC);
        CREATE TRIGGER assessments_updated_at BEFORE UPDATE ON public.assessments
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE TRIGGER assessment_attempts_updated_at BEFORE UPDATE ON public.assessment_attempts
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
    """)
    for table in ("assessments", "assessment_topics", "assessment_subjects", "assessment_attempts"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC,anon,authenticated")
        op.execute(f"GRANT SELECT ON public.{table} TO authenticated")
        op.execute(f"CREATE POLICY {table}_read_own ON public.{table} FOR SELECT TO authenticated USING ((SELECT auth.uid())=user_id)")


def downgrade() -> None:
    raise RuntimeError("Dropping assessment coverage and result history is destructive and requires explicit approval.")
