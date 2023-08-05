# This starts out with https://stackoverflow.com/questions/70392123
import sqlalchemy as sa
from sqlalchemy import MetaData, create_engine, func, select

from lnhub_rest.schema.migrations.function._2023_02_21_a88f5298b8f7_v0_4_2 import (
    sql_functions,
)

# from lnhub_rest.schema.migrations.function._2023_04_04_6e7d7a97c233_v0_8_dev3 import (
#     sql_function_organization,
#     sql_function_update_instance_role,
# )
from lnhub_rest.schema.migrations.rls._2023_02_21_a88f5298b8f7_v0_4_2 import (
    sql_rls_account,
    sql_rls_account_instance,
    sql_rls_instance,
    sql_rls_migration,
    sql_rls_storage,
    sql_rls_version,
)
from lnhub_rest.schema.migrations.rls._2023_03_09_0c4d4fe5f2c6_v0_6_1 import (
    sql_rls_migration as sql_rls_migration_2,
)
from lnhub_rest.schema.migrations.rls._2023_03_09_0c4d4fe5f2c6_v0_6_1 import (
    sql_rls_version as sql_rls_version_2,
)
from lnhub_rest.schema.migrations.rls._2023_03_24_333fd693eac8_v0_6_1b import (
    sql_rls_account_instance_2,
)

# from lnhub_rest.schema.migrations.rls._2023_03_30_b5907be59c45_v0_8_dev1 import (
#     sql_rls_instance_2,
# )
# from lnhub_rest.schema.migrations.rls._2023_04_04_6e7d7a97c233_v0_8_dev3 import (
#     sql_rls_create_org_account,
#     sql_rls_organization_user,
# )


def create_functions_and_rls(db: str):
    engine = sa.create_engine(db, future=True)
    with engine.connect() as conn:
        conn.execute(sa.text(sql_functions))
        conn.execute(sa.text(sql_rls_account))
        conn.execute(sa.text(sql_rls_account_instance))
        conn.execute(sa.text(sql_rls_instance))
        conn.execute(sa.text(sql_rls_migration))
        conn.execute(sa.text(sql_rls_storage))
        conn.execute(sa.text(sql_rls_version))
        conn.execute(sa.text(sql_rls_migration_2))
        conn.execute(sa.text(sql_rls_version_2))
        conn.execute(sa.text(sql_rls_account_instance_2))
        # conn.execute(text(sql_rls_instance_2))
        # conn.execute(text(sql_function_organization))
        # conn.execute(text(sql_function_update_instance_role))
        # conn.execute(text(sql_rls_create_org_account))
        # conn.execute(text(sql_rls_organization_user))
        conn.commit()


def clone_schema(
    schema,
    source_conn,
    source_metadata,
    target_conn,
    target_metadata,
    target_engine,
    n_rows: int,
):
    n_rows_test = n_rows
    # !!! switch off foreign key integrity !!!
    # this is needed because we haven't yet figured out a way to clone connected records
    # might never be needed because we don't want to apply this to large databases
    if source_conn.dialect.name == "postgresql":
        target_conn.execute(sa.sql.text("SET session_replication_role = replica;"))

    # create all tables in target database
    for table in source_metadata.sorted_tables:
        if not sa.inspect(target_engine).has_table(table.name, table.schema):
            table.create(bind=target_engine)
    # refresh metadata before copying data
    target_metadata.clear()
    target_metadata.reflect(bind=target_engine, schema=schema)

    # copy data
    print("Cloning: ", end="")
    for table in target_metadata.sorted_tables:
        if table.schema != schema:
            continue
        source_table = source_metadata.tables[f"{schema}.{table.name}"]
        n_rows = -1  # indicates no rows
        if len(list(source_table.primary_key)) > 0:
            pk_col = getattr(source_table.c, list(source_table.primary_key)[0].name)
            n_rows = int(
                source_conn.execute(
                    select([func.count(pk_col)]).select_from(source_table)
                ).scalar()
            )
        offset = max(n_rows - n_rows_test, 0)
        print(f"{table.name} ({n_rows-offset}/{n_rows})", end=", ")
        rows = source_conn.execute(source_table.select().offset(offset))
        values = [row._asdict() for index, row in enumerate(rows)]
        if len(values) > 0:
            target_conn.execute(table.insert(), values)
            target_conn.commit()


# fixating the number of rows is not a good proxy for getting
# a connected slice of data... not sure whether something better exists
def clone_db(
    *,
    source_db: str,
    target_db: str,
    n_rows: int = 10000,
) -> str:
    """Clone from current instance to a test instance.

    Args:
        source_db: Connection string of source database.
        target_db: Connection string of target database.
        n_rows: Number of rows to clone.
    """
    assert source_db != target_db

    source_engine = create_engine(source_db, future=True)
    source_metadata = MetaData()
    target_engine = create_engine(target_db, future=True)
    target_metadata = MetaData()
    source_conn = source_engine.connect()
    source_metadata.reflect(bind=source_engine)
    target_conn = target_engine.connect()

    # create all schemas in target database
    source_schemas = source_conn.dialect.get_schema_names(source_conn)
    for schemaname in source_schemas:
        if schemaname not in target_conn.dialect.get_schema_names(target_conn):
            target_conn.execute(sa.schema.CreateSchema(schemaname))
        target_conn.commit()

    # only relevant for postgres, clean out some default schemas
    for schema in [
        "information_schema",
        "auth",
        "graphql",
        "graphql_public",
        "realtime",
        "extensions",
        "storage",
    ]:
        if schema in source_schemas:
            source_schemas.remove(schema)

    for schema in source_schemas:
        source_metadata.reflect(bind=source_engine, schema=schema)
        target_metadata.reflect(bind=target_engine, schema=schema)
        if source_engine.dialect.name != "sqlite":
            print(f"\nSchema: {schema}")
        clone_schema(
            schema,
            source_conn,
            source_metadata,
            target_conn,
            target_metadata,
            target_engine,
            n_rows,
        )
    # print a new line
    print("")
    return target_db
