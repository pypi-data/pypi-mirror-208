sql_drop_rls_storage = """
    DROP POLICY "Enable accounts to create storage with their corresponding account id" ON public.storage;

    DROP POLICY "Enable owner to update their storage" ON public.storage;

    DROP POLICY "Enable owner to delete their storage" ON public.storage;
"""  # noqa

sql_reset_rls_storage = """
    CREATE POLICY "Enable accounts to create storage with their corresponding account id"
    ON public.storage
    FOR INSERT
    TO authenticated
    WITH CHECK (
        created_by = auth.uid()
    );

    CREATE POLICY "Enable owner to update their storage"
    ON public.storage
    FOR UPDATE USING (
        created_by = auth.uid()
    )
    WITH CHECK (
        created_by = auth.uid()
    );

    CREATE POLICY "Enable owner to delete their storage"
    ON public.storage
    FOR DELETE USING (
        created_by = auth.uid()
    );
"""  # noqa
