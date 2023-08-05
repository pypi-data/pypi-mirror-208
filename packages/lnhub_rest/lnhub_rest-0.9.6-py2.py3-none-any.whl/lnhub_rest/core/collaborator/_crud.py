from postgrest.exceptions import APIError
from supabase.client import Client


def sb_insert_collaborator(account_instance_fields: dict, supabase_client: Client):
    try:
        (
            supabase_client.table("account_instance")
            .insert(account_instance_fields, returning="minimal")
            .execute()
            .data
        )
    except APIError as api_error:
        pk_violation_msg = (
            'duplicate key value violates unique constraint "pk_account_instance"'
        )
        if api_error.message == pk_violation_msg:
            return "collaborator-exists-already"
        raise api_error
    except Exception as e:
        if str(e) == str("Expecting value: line 1 column 1 (char 0)"):
            pass
        else:
            raise e
    return sb_select_collaborator(
        instance_id=account_instance_fields["instance_id"],
        account_id=account_instance_fields["account_id"],
        supabase_client=supabase_client,
    )


def sb_select_collaborators(
    instance_id: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account_instance")
        .select("*")
        .eq("instance_id", instance_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data


def sb_select_collaborator(
    instance_id: str,
    account_id: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account_instance")
        .select("*")
        .eq("instance_id", instance_id)
        .eq("account_id", account_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data[0]


def sb_update_collaborator(
    instance_id: str,
    account_id: str,
    role: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account_instance")
        .update({"role": role})
        .eq("instance_id", instance_id)
        .eq("account_id", account_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data[0]


def sb_delete_collaborator(
    instance_id: str,
    account_id: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account_instance")
        .delete()
        .eq("instance_id", instance_id)
        .eq("account_id", account_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data[0]


def sb_delete_collaborator_from_all_instances(
    account_id: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account_instance")
        .delete()
        .eq("account_id", account_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data


def sb_delete_all_collaborators_from_instance(
    instance_id: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account_instance")
        .delete()
        .eq("instance_id", instance_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data
