"""Owner-scoped question banks, ordered quizzes and privately frozen attempts."""
from alembic import op

revision = "0006_quizzes"
down_revision = "0005_resources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.questions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            resource_id uuid,
            source_page integer CHECK (source_page BETWEEN 1 AND 200),
            question_type text NOT NULL CHECK (question_type IN ('single_select','multi_select','true_false')),
            prompt text NOT NULL CHECK (btrim(prompt) <> '' AND char_length(prompt) <= 5000),
            explanation text CHECK (char_length(explanation) <= 5000),
            origin text NOT NULL DEFAULT 'manual' CHECK (origin IN ('manual','csv')),
            is_archived boolean NOT NULL DEFAULT false,
            identity_hash text NOT NULL CHECK (identity_hash ~ '^[a-f0-9]{64}$'),
            content_hash text NOT NULL CHECK (content_hash ~ '^[a-f0-9]{64}$'),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (id,user_id), UNIQUE (user_id,identity_hash),
            FOREIGN KEY (topic_id,subject_id) REFERENCES public.topics(id,subject_id),
            FOREIGN KEY (resource_id,user_id) REFERENCES public.resources(id,user_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK (source_page IS NULL OR resource_id IS NOT NULL)
        );
        CREATE INDEX questions_owner_created_idx ON public.questions(user_id,created_at DESC,id DESC);
        CREATE TABLE public.question_options (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            question_id uuid NOT NULL,
            option_key text NOT NULL CHECK (option_key IN ('A','B','C','D','E','F','TRUE','FALSE')),
            text text NOT NULL CHECK (btrim(text) <> '' AND char_length(text) <= 1000),
            is_correct boolean NOT NULL,
            display_order integer NOT NULL CHECK (display_order BETWEEN 0 AND 5),
            UNIQUE (question_id,option_key), UNIQUE(question_id,display_order),
            FOREIGN KEY (question_id,user_id) REFERENCES public.questions(id,user_id) ON DELETE CASCADE
        );
        CREATE TABLE public.quizzes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            title text NOT NULL CHECK (btrim(title) <> '' AND char_length(title) <= 200),
            description text CHECK (char_length(description) <= 2000),
            is_archived boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (id,user_id),
            FOREIGN KEY (topic_id,subject_id) REFERENCES public.topics(id,subject_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL)
        );
        CREATE INDEX quizzes_owner_created_idx ON public.quizzes(user_id,created_at DESC,id DESC);
        CREATE TABLE public.quiz_questions (
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            quiz_id uuid NOT NULL,
            question_id uuid NOT NULL,
            display_order integer NOT NULL CHECK (display_order BETWEEN 0 AND 99),
            PRIMARY KEY (quiz_id,question_id), UNIQUE (quiz_id,display_order),
            FOREIGN KEY (quiz_id,user_id) REFERENCES public.quizzes(id,user_id) ON DELETE CASCADE,
            FOREIGN KEY (question_id,user_id) REFERENCES public.questions(id,user_id)
        );
        CREATE TABLE public.quiz_attempts (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            quiz_id uuid NOT NULL,
            title text NOT NULL,
            status text NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress','completed')),
            snapshot jsonb NOT NULL CHECK (jsonb_typeof(snapshot) = 'array' AND jsonb_array_length(snapshot) BETWEEN 1 AND 100),
            started_at timestamptz NOT NULL DEFAULT now(),
            completed_at timestamptz,
            total_questions integer NOT NULL CHECK (total_questions BETWEEN 1 AND 100),
            score_value integer CHECK (score_value BETWEEN 0 AND total_questions),
            score_percent numeric(5,2) CHECK (score_percent BETWEEN 0 AND 100),
            UNIQUE (id,user_id),
            FOREIGN KEY (quiz_id,user_id) REFERENCES public.quizzes(id,user_id),
            CHECK (jsonb_array_length(snapshot) = total_questions),
            CHECK ((status='in_progress' AND completed_at IS NULL AND score_value IS NULL AND score_percent IS NULL)
                OR (status='completed' AND completed_at IS NOT NULL AND score_value IS NOT NULL AND score_percent IS NOT NULL))
        );
        CREATE UNIQUE INDEX quiz_attempts_one_active_idx ON public.quiz_attempts(user_id,quiz_id) WHERE status='in_progress';
        CREATE INDEX quiz_attempts_owner_started_idx ON public.quiz_attempts(user_id,started_at DESC,id DESC);
        CREATE TABLE public.quiz_answers (
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            attempt_id uuid NOT NULL,
            question_id uuid NOT NULL,
            selected_keys jsonb NOT NULL DEFAULT '[]'::jsonb CHECK (jsonb_typeof(selected_keys)='array' AND jsonb_array_length(selected_keys)<=6),
            is_correct boolean,
            answered_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (attempt_id,question_id),
            FOREIGN KEY (attempt_id,user_id) REFERENCES public.quiz_attempts(id,user_id) ON DELETE CASCADE,
            FOREIGN KEY (question_id,user_id) REFERENCES public.questions(id,user_id)
        );
        CREATE TRIGGER questions_updated_at BEFORE UPDATE ON public.questions FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE TRIGGER quizzes_updated_at BEFORE UPDATE ON public.quizzes FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE FUNCTION public.study_hub_detach_question_sources() RETURNS trigger
        LANGUAGE plpgsql SET search_path = '' AS $$
        BEGIN
            UPDATE public.questions SET resource_id=NULL,source_page=NULL
            WHERE resource_id=OLD.id AND user_id=OLD.user_id;
            RETURN OLD;
        END;
        $$;
        CREATE TRIGGER resources_detach_question_sources BEFORE DELETE ON public.resources
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_detach_question_sources();
    """)
    # Application reads go through FastAPI. No browser grant includes private
    # options, keys, explanation, snapshot, saved answers or grading fields.
    for table in ("questions", "question_options", "quizzes", "quiz_questions", "quiz_attempts", "quiz_answers"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC, anon, authenticated")
        op.execute(f"CREATE POLICY {table}_read_own ON public.{table} FOR SELECT TO authenticated USING ((SELECT auth.uid()) = user_id)")
    op.execute("GRANT SELECT (id,user_id,subject_id,topic_id,resource_id,source_page,question_type,prompt,origin,is_archived,created_at,updated_at) ON public.questions TO authenticated")
    op.execute("GRANT SELECT (id,user_id,subject_id,topic_id,title,description,is_archived,created_at,updated_at) ON public.quizzes TO authenticated")
    op.execute("GRANT SELECT (user_id,quiz_id,question_id,display_order) ON public.quiz_questions TO authenticated")


def downgrade() -> None:
    raise RuntimeError("Dropping private quiz history is destructive and requires explicit approval.")
