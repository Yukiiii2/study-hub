"""Explicit actual-study activity; existing history remains general."""
from alembic import op

revision = "0009_session_activity"
down_revision = "0008_assessments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.study_sessions
            ADD COLUMN activity_type text NOT NULL DEFAULT 'general'
            CONSTRAINT study_sessions_activity_type_check
            CHECK (activity_type IN ('lecture','reading','practice','recall','quiz','general'));
    """)


def downgrade() -> None:
    raise RuntimeError("Removing recorded activity types requires explicit approval.")
