"""v0.8.dev2.

Revision ID: 6e7d7a97c233
Revises: b5907be59c45
Create Date: 2023-04-04 17:20:25.264729

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

from lnhub_rest.schema.migrations.function._2023_04_04_6e7d7a97c233_v0_8_dev2 import (
    sql_reset_functions,
)
from lnhub_rest.schema.migrations.rls._2023_04_04_6e7d7a97c233_v0_8_dev2 import (
    sql_drop_rls_all,
    sql_reset_rls_all,
)

# revision identifiers, used by Alembic.
revision = "6e7d7a97c233"
down_revision = "b5907be59c45"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sql_drop_rls_all)
    op.execute(sql_reset_functions)
    op.execute(sql_reset_rls_all)


def downgrade() -> None:
    pass
