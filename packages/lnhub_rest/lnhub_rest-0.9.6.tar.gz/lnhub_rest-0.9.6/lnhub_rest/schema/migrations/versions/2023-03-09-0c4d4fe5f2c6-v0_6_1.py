"""v0.6.1.

Revision ID: 0c4d4fe5f2c6
Revises: a88f5298b8f7
Create Date: 2023-03-09 09:37:32.028048

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

from lnhub_rest.schema.migrations.rls._2023_03_09_0c4d4fe5f2c6_v0_6_1 import (
    sql_rls_migration,
    sql_rls_version,
)

# revision identifiers, used by Alembic.
revision = "0c4d4fe5f2c6"
down_revision = "a88f5298b8f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sql_rls_migration)
    op.execute(sql_rls_version)


def downgrade() -> None:
    pass
