"""v0.8.dev3.

Revision ID: d0aecf764dbe
Revises: 6e7d7a97c233
Create Date: 2023-04-05 16:19:34.315492

"""
import sqlalchemy as sa  # noqa
import sqlmodel  # noqa
from alembic import op

from lnhub_rest.schema.migrations.function._2023_04_04_6e7d7a97c233_v0_8_dev3 import (
    sql_function_organization,
    sql_function_update_instance_role,
)
from lnhub_rest.schema.migrations.rls._2023_04_04_6e7d7a97c233_v0_8_dev3 import (
    sql_rls_create_org_account,
    sql_rls_organization_user,
)

# revision identifiers, used by Alembic.
revision = "d0aecf764dbe"
down_revision = "6e7d7a97c233"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # create organization_user table
    op.create_table(
        "organization_user",
        sa.Column("organization_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["account.id"],
            name=op.f("fk_organization_user_organization_id_account"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth.users.id"],
            name=op.f("fk_organization_user_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "organization_id", "user_id", name=op.f("pk_organization_user")
        ),
    )
    op.create_index(
        op.f("ix_organization_user_created_at"),
        "organization_user",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_user_organization_id"),
        "organization_user",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_user_updated_at"),
        "organization_user",
        ["updated_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_organization_user_user_id"),
        "organization_user",
        ["user_id"],
        unique=False,
    )

    # drop organization table
    op.drop_table("organization")

    # create role column in account_instance table
    op.add_column(
        "account_instance",
        sa.Column(
            "role",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default="read",
        ),
    )

    # migrate data from permission column to role column in account_instance table
    t_collaborators = sa.Table(
        "account_instance",
        sa.MetaData(),
        sa.Column("account_id", sqlmodel.sql.sqltypes.GUID()),
        sa.Column("instance_id", sqlmodel.sql.sqltypes.GUID()),
        sa.Column("permission", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString()),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )
    conn = op.get_bind()
    results = conn.execute(
        sa.select(
            [
                t_collaborators.c.account_id,
                t_collaborators.c.instance_id,
                t_collaborators.c.permission,
            ]
        )
    ).fetchall()
    for acc_id, ins_id, permission in results:
        if permission == "admin":
            role = "admin"
        elif permission == "read-write":
            role = "write"
        elif permission == "read":
            role = "read"
        conn.execute(
            t_collaborators.update()
            .where(t_collaborators.c.account_id == acc_id)
            .where(t_collaborators.c.instance_id == ins_id)
            .values(role=role)
        )

    # drop role column from account_instance table
    op.drop_column("account_instance", "permission")

    # RLS
    op.execute(sql_function_organization)
    op.execute(sql_function_update_instance_role)
    op.execute(sql_rls_create_org_account)
    op.execute(sql_rls_organization_user)

    # # create lnid column in storage table and dynamically populate values
    op.add_column(
        "storage",
        sa.Column(
            "lnid",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
    )
    op.create_index(op.f("ix_storage_lnid"), "storage", ["lnid"], unique=False)
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM storage")).fetchall()
    for row in rows:
        id = row[0]
        lnid = "00000000"
        conn.execute(sa.text(f"UPDATE storage SET lnid = '{lnid}' WHERE id = '{id}'"))
    op.alter_column("storage", "lnid", nullable=False)

    # change name of account_id column in storage table
    op.alter_column("storage", "account_id", new_column_name="created_by")
    op.drop_index("ix_storage_account_id", table_name="storage")
    op.create_index(
        op.f("ix_storage_created_by"), "storage", ["created_by"], unique=False
    )


def downgrade() -> None:
    pass
