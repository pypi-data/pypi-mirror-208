sql_functions = """
    CREATE OR REPLACE FUNCTION is_instance_member(_account_id uuid, _instance_id uuid) RETURNS boolean
       LANGUAGE plpgsql
       SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN EXISTS (SELECT 1 FROM account_instance AS ai
                      WHERE ai.account_id = _account_id
                      AND ai.instance_id = _instance_id);
    END;$$;


    CREATE OR REPLACE FUNCTION is_instance_admin(_account_id uuid, _instance_id uuid) RETURNS boolean
       LANGUAGE plpgsql
       SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN EXISTS (SELECT 1 FROM account_instance AS ai
                      WHERE ai.account_id = _account_id
                      AND ai.instance_id = _instance_id
                      AND permission = 'admin');
    END;$$;

    CREATE OR REPLACE FUNCTION is_instance_owner(_account_id uuid, _instance_id uuid) RETURNS boolean
       LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
    AS
    $$BEGIN
       RETURN EXISTS (SELECT 1 FROM instance AS i
                      WHERE i.account_id = _account_id
                      AND i.id = _instance_id);
    END;$$;
"""  # noqa
