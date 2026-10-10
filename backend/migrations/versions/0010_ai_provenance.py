"""Preserve confirmed AI draft origin without changing existing study state."""
from alembic import op

revision = "0010_ai_provenance"
down_revision = "0009_session_activity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.questions
            ADD COLUMN ai_provenance jsonb
            CONSTRAINT questions_ai_provenance_check
            CHECK (ai_provenance IS NULL OR jsonb_typeof(ai_provenance) = 'object');
        ALTER TABLE public.questions DROP CONSTRAINT questions_origin_check;
        ALTER TABLE public.questions ADD CONSTRAINT questions_origin_check
            CHECK (origin IN ('manual','csv','ai'));
        ALTER TABLE public.flashcards
            ADD COLUMN ai_provenance jsonb
            CONSTRAINT flashcards_ai_provenance_check
            CHECK (ai_provenance IS NULL OR jsonb_typeof(ai_provenance) = 'object');
    """)


def downgrade() -> None:
    raise RuntimeError("Removing recorded AI provenance requires explicit approval.")
