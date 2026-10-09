"""Private resource originals, metadata and bounded page-aware extracted text."""
from alembic import op

revision = "0005_resources"
down_revision = "0004_study_planner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.resources (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            subject_id uuid REFERENCES public.subjects(id),
            topic_id uuid,
            title text NOT NULL CHECK (btrim(title) <> '' AND char_length(title) <= 200),
            original_filename text NOT NULL CHECK (btrim(original_filename) <> '' AND char_length(original_filename) <= 255),
            mime_type text NOT NULL CHECK (mime_type IN ('application/pdf','text/csv')),
            file_size_bytes integer NOT NULL CHECK (file_size_bytes > 0 AND file_size_bytes <= 4194304),
            storage_bucket text NOT NULL DEFAULT 'study-resources' CHECK (storage_bucket = 'study-resources'),
            storage_path text NOT NULL UNIQUE,
            resource_type text NOT NULL CHECK (resource_type IN ('pdf','csv')),
            processing_status text NOT NULL DEFAULT 'uploaded' CHECK (processing_status IN ('uploaded','processing','ready','failed')),
            page_count integer CHECK (page_count > 0),
            row_count integer CHECK (row_count >= 0),
            error_message text CHECK (char_length(error_message) <= 500),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (id,user_id),
            FOREIGN KEY (topic_id,subject_id) REFERENCES public.topics(id,subject_id),
            CHECK (topic_id IS NULL OR subject_id IS NOT NULL),
            CHECK (storage_path LIKE user_id::text || '/' || id::text || '/%'
                AND storage_path ~ '^[0-9a-f-]{36}/[0-9a-f-]{36}/[A-Za-z0-9 _().-]+[.](pdf|csv)$'),
            CHECK ((resource_type = 'pdf' AND mime_type = 'application/pdf' AND row_count IS NULL)
                OR (resource_type = 'csv' AND mime_type = 'text/csv' AND page_count IS NULL))
        );
        CREATE INDEX resources_owner_created_idx ON public.resources(user_id,created_at DESC,id DESC);
        CREATE INDEX resources_owner_subject_idx ON public.resources(user_id,subject_id,topic_id);
        CREATE TRIGGER resources_updated_at BEFORE UPDATE ON public.resources
            FOR EACH ROW EXECUTE FUNCTION public.study_hub_touch_updated_at();

        CREATE TABLE public.document_sections (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
            resource_id uuid NOT NULL,
            page_number integer NOT NULL CHECK (page_number BETWEEN 1 AND 200),
            section_index integer NOT NULL CHECK (section_index >= 0),
            content text NOT NULL CHECK (char_length(content) <= 20000),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (resource_id,section_index),
            UNIQUE (resource_id,page_number),
            FOREIGN KEY (resource_id,user_id) REFERENCES public.resources(id,user_id) ON DELETE CASCADE
        );
        CREATE INDEX document_sections_owner_resource_idx ON public.document_sections(user_id,resource_id,section_index);
    """)
    for table in ("resources", "document_sections"):
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"REVOKE ALL ON public.{table} FROM PUBLIC, anon, authenticated")
        op.execute(f"GRANT SELECT ON public.{table} TO authenticated")
        op.execute(f"CREATE POLICY {table}_read_own ON public.{table} FOR SELECT TO authenticated "
                   "USING ((SELECT auth.uid()) = user_id)")
    # Only the Storage API creates the private bucket. SQL never edits Storage metadata.
    op.execute("""
        CREATE POLICY study_resources_read_own ON storage.objects FOR SELECT TO authenticated
        USING (
            bucket_id = 'study-resources'
            AND (storage.foldername(name))[1] = (SELECT auth.uid())::text
            AND EXISTS (
                SELECT 1 FROM public.resources r
                WHERE r.user_id = (SELECT auth.uid()) AND r.storage_bucket = bucket_id AND r.storage_path = name
            )
        );
    """)


def downgrade() -> None:
    raise RuntimeError("Dropping private resource data is destructive and requires explicit approval.")
