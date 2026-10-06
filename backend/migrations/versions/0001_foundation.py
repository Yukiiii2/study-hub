"""Supabase profiles and curriculum structure with RLS."""

from alembic import op

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.profiles (
            id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
            display_name text,
            timezone text NOT NULL DEFAULT 'Asia/Manila' CHECK (btrim(timezone) <> ''),
            target_exam_date date,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE public.subjects (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            code text NOT NULL UNIQUE CHECK (btrim(code) <> ''),
            name text NOT NULL CHECK (btrim(name) <> ''),
            display_order integer NOT NULL DEFAULT 0 CHECK (display_order >= 0),
            color_key text,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        );
        CREATE TABLE public.topics (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            subject_id uuid NOT NULL REFERENCES public.subjects(id),
            parent_topic_id uuid,
            code text,
            title text NOT NULL CHECK (btrim(title) <> ''),
            description text,
            display_order integer NOT NULL DEFAULT 0 CHECK (display_order >= 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (id, subject_id),
            FOREIGN KEY (parent_topic_id, subject_id) REFERENCES public.topics(id, subject_id),
            CHECK (parent_topic_id IS DISTINCT FROM id)
        );
        CREATE INDEX topics_subject_id_idx ON public.topics(subject_id);
        CREATE INDEX topics_parent_topic_id_idx ON public.topics(parent_topic_id);

        -- Serialize hierarchy writes so concurrent reparenting cannot create a cycle.
        CREATE FUNCTION public.study_hub_lock_topics()
        RETURNS trigger LANGUAGE plpgsql SET search_path = '' AS $$
        BEGIN
            LOCK TABLE public.topics IN SHARE ROW EXCLUSIVE MODE;
            RETURN NULL;
        END;
        $$;
        CREATE TRIGGER topics_hierarchy_lock BEFORE INSERT OR UPDATE ON public.topics
            FOR EACH STATEMENT EXECUTE FUNCTION public.study_hub_lock_topics();
        CREATE FUNCTION public.study_hub_check_topic_parent()
        RETURNS trigger LANGUAGE plpgsql SET search_path = '' AS $$
        BEGIN
            IF EXISTS (
                WITH RECURSIVE ancestors AS (
                    SELECT id, parent_topic_id FROM public.topics WHERE id = NEW.parent_topic_id
                    UNION
                    SELECT t.id, t.parent_topic_id FROM public.topics t
                    JOIN ancestors a ON t.id = a.parent_topic_id
                ) SELECT 1 FROM ancestors WHERE id = NEW.id
            ) THEN
                RAISE EXCEPTION 'Topic parent relationships must not contain a cycle';
            END IF;
            RETURN NEW;
        END;
        $$;
        CREATE CONSTRAINT TRIGGER topics_parent_acyclic AFTER INSERT OR UPDATE ON public.topics
            DEFERRABLE INITIALLY IMMEDIATE FOR EACH ROW
            EXECUTE FUNCTION public.study_hub_check_topic_parent();

        CREATE FUNCTION public.study_hub_touch_updated_at()
        RETURNS trigger LANGUAGE plpgsql SET search_path = '' AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;
        CREATE TRIGGER profiles_updated_at BEFORE UPDATE ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE TRIGGER subjects_updated_at BEFORE UPDATE ON public.subjects
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();
        CREATE TRIGGER topics_updated_at BEFORE UPDATE ON public.topics
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();

        CREATE FUNCTION public.study_hub_create_profile()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
        BEGIN
            INSERT INTO public.profiles(id) VALUES (NEW.id) ON CONFLICT (id) DO NOTHING;
            RETURN NEW;
        END;
        $$;
        REVOKE ALL ON FUNCTION public.study_hub_create_profile() FROM PUBLIC, anon, authenticated;
        CREATE TRIGGER study_hub_auth_user_created AFTER INSERT ON auth.users
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_create_profile();
        INSERT INTO public.profiles(id) SELECT id FROM auth.users ON CONFLICT (id) DO NOTHING;

        ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
        ALTER TABLE public.topics ENABLE ROW LEVEL SECURITY;
        REVOKE ALL ON public.profiles, public.subjects, public.topics FROM PUBLIC, anon, authenticated;
        GRANT SELECT ON public.profiles TO authenticated;
        GRANT UPDATE (display_name, timezone, target_exam_date) ON public.profiles TO authenticated;
        GRANT SELECT ON public.subjects, public.topics TO authenticated;

        CREATE POLICY profiles_read_own ON public.profiles FOR SELECT TO authenticated
            USING ((SELECT auth.uid()) = id);
        CREATE POLICY profiles_update_own ON public.profiles FOR UPDATE TO authenticated
            USING ((SELECT auth.uid()) = id) WITH CHECK ((SELECT auth.uid()) = id);
        CREATE POLICY subjects_read_authenticated ON public.subjects FOR SELECT TO authenticated
            USING (true);
        CREATE POLICY topics_read_authenticated ON public.topics FOR SELECT TO authenticated
            USING (true);
    """)


def downgrade() -> None:
    raise RuntimeError("Dropping foundation tables is destructive and requires explicit approval.")
