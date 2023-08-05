sql_rls_migration = "ALTER TABLE migration_cbwk ENABLE ROW LEVEL SECURITY;"

sql_rls_version = "ALTER TABLE version_cbwk ENABLE ROW LEVEL SECURITY;"

sql_rls_account = """
    ALTER TABLE account ENABLE ROW LEVEL SECURITY;

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

sql_rls_storage = """
    ALTER TABLE storage ENABLE ROW LEVEL SECURITY;

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

sql_rls_instance = """
    ALTER TABLE instance ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "Enable everyone to select public instances"
    ON public.instance
    FOR SELECT USING (
        public = true
    );

    CREATE POLICY "Enable members to select their instances"
    ON public.instance
    FOR SELECT USING (
        is_instance_member(auth.uid(), id)
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

    CREATE POLICY "Enable admin accounts to update their instances"
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
"""  # noqa

sql_rls_account_instance = """
    ALTER TABLE account_instance ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "Enable owner to add collaborators"
    ON public.account_instance
    AS PERMISSIVE
    FOR INSERT
    WITH CHECK (
      is_instance_owner(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable admin accounts to add collaborators"
    ON public.account_instance
    FOR INSERT
    WITH CHECK (
        is_instance_admin(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable admin to update collaborators"
    ON public.account_instance
    FOR UPDATE USING (
        is_instance_admin(auth.uid(), instance_id)
    )
    WITH CHECK (
        is_instance_admin(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable admin to delete collaborators"
    ON public.account_instance
    FOR DELETE USING (
        is_instance_admin(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable owner to delete collaborators"
    ON public.account_instance
    FOR DELETE USING (
        is_instance_owner(auth.uid(), instance_id)
    );

    CREATE POLICY "Enable members to select members of their instances"
    ON public.account_instance
    FOR SELECT USING (
        is_instance_member(auth.uid(), instance_id)
    );
"""  # noqa
