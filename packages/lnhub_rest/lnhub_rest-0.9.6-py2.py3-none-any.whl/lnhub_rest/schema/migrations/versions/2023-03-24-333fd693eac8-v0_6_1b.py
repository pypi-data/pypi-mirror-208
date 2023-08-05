"""v0.6.1b.

Revision ID: 333fd693eac8
Revises: 0c4d4fe5f2c6
Create Date: 2023-03-24 16:27:30.558105

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

from lnhub_rest.schema.migrations.rls._2023_03_24_333fd693eac8_v0_6_1b import (
    sql_rls_account_instance_2,
)

# revision identifiers, used by Alembic.
revision = "333fd693eac8"
down_revision = "0c4d4fe5f2c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sql_rls_account_instance_2)


def downgrade() -> None:
    pass
