sql_rls_account_instance_2 = """
    CREATE POLICY "Enable owner to select collaborators"
    ON public.account_instance
    FOR SELECT USING (
        is_instance_owner(auth.uid(), instance_id)
    );
"""  # noqa
