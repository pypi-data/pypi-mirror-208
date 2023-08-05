# Migrations

1. Set env: `export LN_SERVER_DEPLOY=1` and `export LNHUB_PROD_PG_PASSWORD=***`
2. Modify the schema by rewriting the ORMs (add a column, rename a column, add constraints, drop constraints, add an ORM, etc.)
3. Generate the migration script: `lnhub migrate generate`
4. Thoroughly test the migration script: `pytest tests/test_migrations.py`
5. Once tests pass, merge to main and make a release commit, **bump** the version number
6. Deploy the migration to production database via `lnhub migrate deploy`.
