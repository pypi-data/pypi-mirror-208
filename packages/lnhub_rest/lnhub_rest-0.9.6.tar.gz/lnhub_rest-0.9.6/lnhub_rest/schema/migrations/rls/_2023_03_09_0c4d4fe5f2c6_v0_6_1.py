sql_rls_migration = """
    CREATE POLICY "Enable everyone to see a migration"
    ON public.migration_cbwk
    FOR SELECT USING (
        true
    );

    CREATE POLICY "Enable everyone to create an entry in migration_cbwk table"
    ON public.migration_cbwk
    FOR INSERT
    WITH CHECK (
        true
    );
"""  # noqa

sql_rls_version = """
    CREATE POLICY "Enable everyone to see a version"
    ON public.version_cbwk
    FOR SELECT USING (
        true
    );

    CREATE POLICY "Enable everyone to create an entry in version_cbwk table"
    ON public.version_cbwk
    FOR INSERT
    WITH CHECK (
        true
    );
"""  # noqa
