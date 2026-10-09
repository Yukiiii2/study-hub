"""Private cards, current recall state and immutable review history."""
from alembic import op

revision = "0007_flashcards"
down_revision = "0006_quizzes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.flashcard_decks (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid REFERENCES public.subjects(id),
            title text NOT NULL CHECK (btrim(title) <> '' AND char_length(title) <= 200),
            description text CHECK (char_length(description) <= 2000),
            is_archived boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE(id,user_id)
        );
        CREATE INDEX flashcard_decks_owner_created_idx ON public.flashcard_decks(user_id,created_at DESC,id DESC);
        CREATE TABLE public.flashcards (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            deck_id uuid,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            resource_id uuid,
            source_page integer CHECK (source_page BETWEEN 1 AND 200),
            front text NOT NULL CHECK (btrim(front) <> '' AND char_length(front) <= 5000),
            back text NOT NULL CHECK (btrim(back) <> '' AND char_length(back) <= 12000),
            notes text CHECK (char_length(notes) <= 5000),
            status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','archived')),
            interval_days integer NOT NULL DEFAULT 0 CHECK (interval_days BETWEEN 0 AND 365),
            next_review_at timestamptz NOT NULL DEFAULT now(),
            review_revision bigint NOT NULL DEFAULT 0 CHECK (review_revision >= 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE(id,user_id),
            FOREIGN KEY (deck_id,user_id) REFERENCES public.flashcard_decks(id,user_id),
            FOREIGN KEY (topic_id,subject_id) REFERENCES public.topics(id,subject_id),
            FOREIGN KEY (resource_id,user_id) REFERENCES public.resources(id,user_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK (source_page IS NULL OR resource_id IS NOT NULL)
        );
        CREATE INDEX flashcards_owner_created_idx ON public.flashcards(user_id,created_at DESC,id DESC);
        CREATE INDEX flashcards_owner_due_idx ON public.flashcards(user_id,next_review_at,id) WHERE status='active';
        CREATE INDEX flashcards_owner_deck_idx ON public.flashcards(user_id,deck_id);
        CREATE INDEX flashcards_owner_subject_topic_idx ON public.flashcards(user_id,subject_id,topic_id);
        CREATE INDEX flashcards_owner_source_idx ON public.flashcards(user_id,resource_id);
        CREATE TABLE public.flashcard_reviews (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            flashcard_id uuid NOT NULL,
            request_id uuid NOT NULL,
            previous_revision bigint NOT NULL CHECK (previous_revision >= 0),
            reviewed_at timestamptz NOT NULL,
            rating text NOT NULL CHECK (rating IN ('again','hard','good','easy')),
            previous_interval_days integer NOT NULL CHECK (previous_interval_days BETWEEN 0 AND 365),
            next_interval_days integer NOT NULL CHECK (next_interval_days BETWEEN 0 AND 365),
            next_review_at timestamptz NOT NULL CHECK (next_review_at > reviewed_at),
            algorithm_version text NOT NULL CHECK (algorithm_version='recall-v1'),
            front_snapshot text NOT NULL CHECK (char_length(front_snapshot) BETWEEN 1 AND 5000),
            back_snapshot text NOT NULL CHECK (char_length(back_snapshot) BETWEEN 1 AND 12000),
            created_at timestamptz NOT NULL DEFAULT now(),
            FOREIGN KEY (flashcard_id,user_id) REFERENCES public.flashcards(id,user_id),
            UNIQUE(user_id,request_id), UNIQUE(flashcard_id,previous_revision)
        );
        CREATE INDEX flashcard_reviews_owner_card_idx ON public.flashcard_reviews(user_id,flashcard_id,reviewed_at DESC,id DESC);
        CREATE TRIGGER flashcard_decks_updated_at BEFORE UPDATE ON public.flashcard_decks
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE TRIGGER flashcards_updated_at BEFORE UPDATE ON public.flashcards
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE FUNCTION public.study_hub_detach_flashcard_sources() RETURNS trigger
        LANGUAGE plpgsql SET search_path = '' AS $$
        BEGIN
            PERFORM id FROM public.flashcards WHERE resource_id=OLD.id AND user_id=OLD.user_id
            ORDER BY id FOR UPDATE;
            UPDATE public.flashcards SET resource_id=NULL,source_page=NULL,review_revision=review_revision+1
            WHERE resource_id=OLD.id AND user_id=OLD.user_id;
            RETURN OLD;
        END;
        $$;
        REVOKE ALL ON FUNCTION public.study_hub_detach_flashcard_sources() FROM PUBLIC,anon,authenticated;
        CREATE TRIGGER resources_detach_flashcard_sources BEFORE DELETE ON public.resources
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_detach_flashcard_sources();
    """)
    for table in ("flashcard_decks", "flashcards", "flashcard_reviews"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC,anon,authenticated")
        op.execute(f"GRANT SELECT ON public.{table} TO authenticated")
        op.execute(f"CREATE POLICY {table}_read_own ON public.{table} FOR SELECT TO authenticated USING ((SELECT auth.uid())=user_id)")


def downgrade() -> None:
    raise RuntimeError("Dropping private recall history is destructive and requires explicit approval.")
