sql_drop_rls_account = """
    DROP POLICY "Enable everyone to see an account" ON public.account;

    DROP POLICY "Enable accounts to create a corresponding entry in account table" ON public.account;

    DROP POLICY "Enable accounts to update their data" ON public.account;

    DROP POLICY "Enable accounts to delete their entry in account table" ON public.account;
"""  # noqa

sql_reset_rls_account = """
    CREATE POLICY "Enable everyone to see an account"
    ON public.account
    FOR SELECT USING (
        true
    );

    CREATE POLICY "Enable accounts to create a corresponding entry in account table"
    ON public.account
    FOR INSERT
    WITH CHECK (
        id = auth.uid()
    );

    CREATE POLICY "Enable accounts to update their data"
    ON public.account
    FOR UPDATE USING (
        id = auth.uid()
    )
    WITH CHECK (
        id = auth.uid()
    );

    CREATE POLICY "Enable accounts to delete their entry in account table"
    ON public.account
    FOR DELETE USING (
        id = auth.uid()
    );
"""  # noqa

sql_drop_rls_storage = """
    DROP POLICY "Enable accounts to create storage with their corresponding account id" ON public.storage;

    DROP POLICY "Enable owner to update their storage" ON public.storage;

    DROP POLICY "Enable owner to delete their storage" ON public.storage;

    DROP POLICY "Enable everyone to select a storage" on public.storage;
"""  # noqa

sql_reset_rls_storage = """
    CREATE POLICY "Enable accounts to create storage with their corresponding account id"
    ON public.storage
    FOR INSERT
    TO authenticated
    WITH CHECK (
        account_id = auth.uid()
    );

    CREATE POLICY "Enable owner to update their storage"
    ON public.storage
    FOR UPDATE USING (
        account_id = auth.uid()
    )
    WITH CHECK (
        account_id = auth.uid()
    );

    CREATE POLICY "Enable owner to delete their storage"
    ON public.storage
    FOR DELETE USING (
        account_id = auth.uid()
    );

    CREATE POLICY "Enable everyone to select a storage"
    ON public.storage
    FOR SELECT USING (
        true
    );
"""  # noqa

sql_drop_rls_instance = """
    DROP POLICY "Enable everyone to select public instances" ON public.instance;

    DROP POLICY "Enable members to select their instances" ON public.instance;

    DROP POLICY "Enable owners to select their instances" ON public.instance;

    DROP POLICY "Enable authenticated accounts to create instance" ON public.instance;

    DROP POLICY "Enable admin accounts to update their instances" ON public.instance;

    DROP POLICY "Enable owners to delete their instances" ON public.instance;

    DROP POLICY "Enable admins to delete their instances" ON public.instance;
"""  # noqa

sql_reset_rls_instance = """
    CREATE POLICY "Enable everyone to select public instances"
    ON public.instance
    FOR SELECT USING (
        public = true
    );

    CREATE POLICY "Enable collaborators to select their instances"
    ON public.instance
    FOR SELECT USING (
        is_instance_collaborator(auth.uid(), id)
    );

    CREATE POLICY "Enable owners to select their instances"
    ON public.instance
    FOR SELECT USING (
        is_instance_owner(auth.uid(), id)
    );

    CREATE POLICY "Enable authenticated accounts to create instance"
    ON public.instance
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

    CREATE POLICY "Enable admin collaborators to update their instances"
    ON public.instance
    FOR UPDATE USING (
        is_instance_admin(auth.uid(), id)
    )
    WITH CHECK (
        is_instance_admin(auth.uid(), id)
    );

    CREATE POLICY "Enable owners to delete their instances"
    ON public.instance
    FOR DELETE USING (
        is_instance_owner(auth.uid(), id)
    );

    CREATE POLICY "Enable admin collaborators to delete their instances"
    ON public.instance
    FOR DELETE USING (
        is_instance_admin(auth.uid(), id)
    );
"""  # noqa

sql_drop_rls_account_instance = """
    DROP POLICY "Enable owner to add collaborators" ON public.account_instance;

    DROP POLICY "Enable admin accounts to add collaborators" ON public.account_instance;

    DROP POLICY "Enable admin to update collaborators" ON public.account_instance;

    DROP POLICY "Enable admin to delete collaborators" ON public.account_instance;

    DROP POLICY "Enable owner to delete collaborators" ON public.account_instance;

    DROP POLICY "Enable members to select members of their instances" ON public.account_instance;

    DROP POLICY "Enable owner to select collaborators" ON public.account_instance;
"""  # noqa

sql_reset_rls_account_instance = """
    CREATE POLICY "Enable owner to add collaborators"
    ON public.account_instance
    AS PERMISSIVE
    FOR INSERT
    WITH CHECK (
      is_instance_owner(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable admin collaborators to add collaborators"
    ON public.account_instance
    FOR INSERT
    WITH CHECK (
        is_instance_admin(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable admin collaborators to update collaborators"
    ON public.account_instance
    FOR UPDATE USING (
        is_instance_admin(auth.uid(), instance_id)
    )
    WITH CHECK (
        is_instance_admin(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable admin collaborators to delete collaborators"
    ON public.account_instance
    FOR DELETE USING (
        is_instance_admin(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable instance owner to delete collaborators"
    ON public.account_instance
    FOR DELETE USING (
        is_instance_owner(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable collaborators to select collaborators of their instances"
    ON public.account_instance
    FOR SELECT USING (
        is_instance_collaborator(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable instance owner to select collaborators"
    ON public.account_instance
    FOR SELECT USING (
        is_instance_owner(auth.uid(), instance_id)
    );
"""  # noqa

sql_drop_rls_migration = """
    DROP POLICY "Enable everyone to see a migration" ON public.migration_cbwk;

    DROP POLICY "Enable everyone to create an entry in migration_cbwk table" ON public.migration_cbwk;
"""  # noqa

sql_reset_rls_migration = """
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

sql_drop_rls_version = """
    DROP POLICY "Enable everyone to see a version" ON public.version_cbwk;

    DROP POLICY "Enable everyone to create an entry in version_cbwk table" ON public.version_cbwk;
"""  # noqa

sql_reset_rls_version = """
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

sql_drop_rls_all = "\n\n".join(
    [
        sql_drop_rls_account,
        sql_drop_rls_storage,
        sql_drop_rls_instance,
        sql_drop_rls_account_instance,
        sql_drop_rls_migration,
        sql_drop_rls_version,
    ]
)

sql_reset_rls_all = "\n\n".join(
    [
        sql_reset_rls_account,
        sql_reset_rls_storage,
        sql_reset_rls_instance,
        sql_reset_rls_account_instance,
        sql_reset_rls_migration,
        sql_reset_rls_version,
    ]
)
