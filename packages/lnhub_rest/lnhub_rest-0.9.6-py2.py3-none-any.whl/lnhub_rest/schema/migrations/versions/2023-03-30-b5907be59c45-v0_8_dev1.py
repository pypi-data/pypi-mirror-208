"""v0.8.dev1.

Revision ID: b5907be59c45
Revises: 333fd693eac8
Create Date: 2023-03-30 17:35:52.404091

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

from lnhub_rest.schema.migrations.rls._2023_03_30_b5907be59c45_v0_8_dev1 import (
    sql_rls_instance_2,
)

# revision identifiers, used by Alembic.
revision = "b5907be59c45"
down_revision = "333fd693eac8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_account_instance_account_id_account", "account_instance", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_account_instance_instance_id_instance",
        "account_instance",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_account_instance_account_id_account"),
        "account_instance",
        "account",
        ["account_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        op.f("fk_account_instance_instance_id_instance"),
        "account_instance",
        "instance",
        ["instance_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(sql_rls_instance_2)


def downgrade() -> None:
    pass
