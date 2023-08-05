"""v0.4.2.

Revision ID: a88f5298b8f7
Revises: 1fdc05837919
Create Date: 2023-02-21 16:57:39.955871

"""
import sqlalchemy as sa  # noqa
from alembic import op

from lnhub_rest.schema.migrations.function._2023_02_21_a88f5298b8f7_v0_4_2 import (
    sql_functions,
)
from lnhub_rest.schema.migrations.rls._2023_02_21_a88f5298b8f7_v0_4_2 import (
    sql_rls_account,
    sql_rls_account_instance,
    sql_rls_instance,
    sql_rls_migration,
    sql_rls_storage,
    sql_rls_version,
)

# revision identifiers, used by Alembic.
revision = "a88f5298b8f7"
down_revision = "1fdc05837919"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sql_functions)
    op.execute(sql_rls_migration)
    op.execute(sql_rls_version)
    op.execute(sql_rls_account)
    op.execute(sql_rls_storage)
    op.execute(sql_rls_instance)
    op.execute(sql_rls_account_instance)


def downgrade() -> None:
    pass
