"""v0.8.1.

Revision ID: 1092ae46baba
Revises: d0aecf764dbe
Create Date: 2023-04-18 11:01:05.582866

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

from lnhub_rest.schema.migrations.rls._2023_04_18_1092ae46baba_v0_8_1 import (
    sql_drop_rls_storage,
    sql_reset_rls_storage,
)

# revision identifiers, used by Alembic.
revision = "1092ae46baba"
down_revision = "d0aecf764dbe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sql_drop_rls_storage)
    op.execute(sql_reset_rls_storage)


def downgrade() -> None:
    pass
