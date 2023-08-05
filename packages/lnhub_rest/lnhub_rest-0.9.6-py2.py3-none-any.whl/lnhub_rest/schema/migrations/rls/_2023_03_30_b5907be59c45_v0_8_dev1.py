sql_rls_instance_2 = """
    CREATE POLICY "Enable admins to delete their instances"
    ON public.instance
    FOR DELETE USING (
        is_instance_admin(auth.uid(), id)
    );
"""  # noqa
