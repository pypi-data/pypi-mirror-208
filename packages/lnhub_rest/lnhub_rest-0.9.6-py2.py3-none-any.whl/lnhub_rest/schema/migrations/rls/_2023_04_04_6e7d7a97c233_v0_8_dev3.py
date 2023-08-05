sql_rls_create_org_account = """
    DROP POLICY "Enable accounts to create a corresponding entry in account table" ON public.account;

    CREATE POLICY "Enable authenticated accounts to create an entry in the account table"
    ON public.account
    FOR INSERT
    TO authenticated
    WITH CHECK (true);
"""  # noqa

sql_rls_organization_user = """
    ALTER TABLE public.organization_user ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "Enable authenticated accounts to add themselves to an empty organization"
    ON public.organization_user
    FOR INSERT
    TO authenticated
    WITH CHECK (
        is_organization_empty(organization_id)
        AND user_id = auth.uid()
    );

    CREATE POLICY "Enable owners to add members"
    ON public.organization_user
    FOR INSERT
    WITH CHECK (
        is_organization_owner(auth.uid(), organization_id)
    );

    CREATE POLICY "Enable owners to update members"
    ON public.organization_user
    FOR UPDATE USING (
        is_organization_owner(auth.uid(), organization_id)
    );

    CREATE POLICY "Enable owners to delete members"
    ON public.organization_user
    FOR DELETE USING (
        is_organization_owner(auth.uid(), organization_id)
    );

    CREATE POLICY "Enable members to select other members"
    ON public.organization_user
    FOR SELECT USING (
        is_organization_member(auth.uid(), organization_id)
    );
"""  # noqa
