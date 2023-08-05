# some of the logic here is also present in lndb.test._migrations_unit
import io
from pathlib import Path
from typing import Optional

import sqlalchemy as sa
from alembic import command
from alembic.autogenerate.api import AutogenContext
from alembic.autogenerate.render import _render_cmd_body
from pytest_alembic.config import Config
from pytest_alembic.executor import CommandExecutor, ConnectionExecutor
from pytest_alembic.plugin.error import AlembicTestFailure
from pytest_alembic.runner import MigrationContext
from sqlmodel import SQLModel

from lnhub_rest.config import Settings

SCHEMA_PACKAGE_LOC = Path(__file__).parent.parent.resolve().as_posix()


def migration_id_is_consistent():
    migration_id = get_migration_id_from_scripts()
    from lnhub_rest.schema import _migration

    if _migration is None:
        manual_migration_id = ""
    else:
        manual_migration_id = _migration
    return manual_migration_id == migration_id


def model_definitions_match_ddl(*, test_db: Optional[str] = None):
    # The main part of this function is largely copied from the
    # MIT licensed https://github.com/schireson/pytest-alembic
    """Assert that the state of the migrations matches the state of the models.

    Args:
        test_db: Connection string of test database on which to perform migrations.
        clone: Create a test database from a clone of the production database.

    In general, the set of migrations in the history should coalesce into DDL
    which is described by the current set of models. Therefore, a call to
    `revision --autogenerate` should always generate an empty migration (e.g.
    find no difference between your database (i.e. migrations history) and your
    models).
    """
    # @lawrlee this should be handled upstream
    if test_db is None:
        settings = Settings()
        test_db = settings.postgres_dsn

    alembic_runner = get_migration_context(test_db)

    def verify_is_empty_revision(migration_context, __, directives):
        script = directives[0]

        migration_is_empty = script.upgrade_ops.is_empty()
        if not migration_is_empty:
            autogen_context = AutogenContext(migration_context)
            rendered_upgrade = _render_cmd_body(script.upgrade_ops, autogen_context)

            if not migration_is_empty:
                raise AlembicTestFailure(
                    "The models describing the DDL of your database are out of sync"
                    " with the set of steps described in the revision history. This"
                    " usually means that someone has made manual changes to the"
                    " database's DDL, or some model has been changed without also"
                    " generating a migration to describe that"
                    f" change.\n{rendered_upgrade}"
                )

    try:
        alembic_runner.migrate_up_to("heads")
    except RuntimeError as e:
        raise AlembicTestFailure(
            "Failed to upgrade to the head revision. This means the historical chain"
            f" from an empty database, to the current revision is not possible.\n{e}"
        )

    alembic_runner.generate_revision(
        message="test revision",
        autogenerate=True,
        prevent_file_generation=True,
        process_revision_directives=verify_is_empty_revision,
    )


def get_migration_context(connection_string):
    engine = sa.create_engine(connection_string, future=True)
    target_metadata = SQLModel.metadata
    config = get_migration_config(
        target_metadata=target_metadata,
        include_schemas=True,
        include_name=include_name,
    )
    command_executor = CommandExecutor.from_config(config)
    command_executor.configure(connection=engine)
    migration_context = MigrationContext.from_config(
        config, command_executor, ConnectionExecutor(), engine
    )
    return migration_context


def get_migration_config(*, target_metadata=None, **kwargs):
    if target_metadata is None:
        target_metadata = SQLModel.metadata
    target_metadata.naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    raw_config = dict(
        config_file_name=f"{SCHEMA_PACKAGE_LOC}/alembic.ini",
        script_location=f"{SCHEMA_PACKAGE_LOC}/migrations",
        target_metadata=target_metadata,
        **kwargs,
    )
    config = Config.from_raw_config(raw_config)
    return config


def get_migration_id_from_scripts():
    config = get_migration_config()
    output_buffer = io.StringIO()
    # get the id of the latest migration script
    if Path(f"{SCHEMA_PACKAGE_LOC}/migrations/versions").exists():
        command.heads(config.make_alembic_config(stdout=output_buffer))
        output = output_buffer.getvalue()
        migration_id = output.split(" ")[0]
    else:  # there is no scripts directory
        migration_id = ""
    return migration_id


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in {None, "core"}  # only consider public schema
    else:
        return True
