"""Seed the seven CPA subjects, without topic or user data."""

from alembic import op

revision = "0002_seed_subjects"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO public.subjects (id, code, name, display_order) VALUES
            ('00000000-0000-4000-8000-000000000001', 'FAR', 'Financial Accounting and Reporting', 1),
            ('00000000-0000-4000-8000-000000000002', 'AFAR', 'Advanced Financial Accounting and Reporting', 2),
            ('00000000-0000-4000-8000-000000000003', 'MAS', 'Management Advisory Services', 3),
            ('00000000-0000-4000-8000-000000000004', 'TAX', 'Taxation', 4),
            ('00000000-0000-4000-8000-000000000005', 'RFBT', 'Regulatory Framework for Business Transactions', 5),
            ('00000000-0000-4000-8000-000000000006', 'AT', 'Auditing Theory', 6),
            ('00000000-0000-4000-8000-000000000007', 'AP', 'Auditing Problems', 7)
        ON CONFLICT (code) DO NOTHING;
    """)


def downgrade() -> None:
    raise RuntimeError("Deleting seeded curriculum is destructive and requires explicit approval.")
