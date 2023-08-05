from supabase.client import Client


def sb_insert_account(
    account_fields: dict,
    supabase_client: Client,
):
    data = supabase_client.table("account").insert(account_fields).execute().data
    if len(data) == 0:
        return None
    return data[0]


def sb_update_account(
    account_id: str,
    account_fields: dict,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account")
        .update(account_fields)
        .eq("id", account_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data[0]


def sb_select_account_by_handle(
    handle: str,
    supabase_client: Client,
):
    data = (
        supabase_client.table("account").select("*").eq("handle", handle).execute().data
    )
    if len(data) == 0:
        return None
    return data[0]


def sb_delete_account(
    handle: str,
    supabase_client: Client,
):
    data = supabase_client.table("account").delete().eq("handle", handle).execute().data
    if len(data) == 0:
        return None
    return data[0]
