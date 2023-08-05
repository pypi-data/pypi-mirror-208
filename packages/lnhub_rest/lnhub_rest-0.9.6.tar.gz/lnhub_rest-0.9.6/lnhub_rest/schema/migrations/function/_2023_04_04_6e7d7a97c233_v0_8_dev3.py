sql_function_organization = """
    CREATE OR REPLACE FUNCTION is_organization_empty(_organization_id uuid) RETURNS boolean
       LANGUAGE plpgsql
       SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN NOT EXISTS (SELECT 1 FROM organization_user AS ai
                          WHERE ai.organization_id = _organization_id);
    END;$$;

    CREATE OR REPLACE FUNCTION is_organization_owner(_user_id uuid, _organization_id uuid) RETURNS boolean
       LANGUAGE plpgsql
       SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN EXISTS (SELECT 1 FROM organization_user AS ai
                      WHERE ai.user_id = _user_id
                      AND ai.organization_id = _organization_id
                      AND role = 'owner');
    END;$$;

    CREATE OR REPLACE FUNCTION is_organization_member(_user_id uuid, _organization_id uuid) RETURNS boolean
       LANGUAGE plpgsql
       SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN EXISTS (SELECT 1 FROM organization_user AS ai
                      WHERE ai.user_id = _user_id
                      AND ai.organization_id = _organization_id);
    END;$$;
"""  # noqa

sql_function_update_instance_role = """
    CREATE OR REPLACE FUNCTION is_instance_admin(_account_id uuid, _instance_id uuid) RETURNS boolean
       LANGUAGE plpgsql
       SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN EXISTS (SELECT 1 FROM account_instance AS ai
                      WHERE ai.account_id = _account_id
                      AND ai.instance_id = _instance_id
                      AND role = 'admin');
    END;$$;
"""  # noqa
