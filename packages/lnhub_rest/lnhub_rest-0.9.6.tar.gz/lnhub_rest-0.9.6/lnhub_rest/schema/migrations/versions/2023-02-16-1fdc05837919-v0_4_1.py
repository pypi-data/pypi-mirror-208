"""v0.4.1.

Revision ID: 1fdc05837919
Revises: 8d91d067cc7d
Create Date: 2023-02-16 13:36:31.449643

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1fdc05837919"
down_revision = "8d91d067cc7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "version_cbwk",
        sa.Column("breaks_lndb", sa.Boolean(), nullable=True),
    )
    op.execute("update version_cbwk set breaks_lndb = false")
    op.alter_column("version_cbwk", "breaks_lndb", nullable=False)


def downgrade() -> None:
    pass
