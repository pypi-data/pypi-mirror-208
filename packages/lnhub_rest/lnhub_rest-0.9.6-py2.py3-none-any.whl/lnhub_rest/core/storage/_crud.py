from supabase.client import Client


def sb_insert_storage(storage_fields: dict, supabase_client: Client):
    data = supabase_client.table("storage").insert(storage_fields).execute().data
    if len(data) == 0:
        return None
    return data[0]


def sb_udpate_storage(id: str, storage_fields: dict, supabase_client: Client):
    data = (
        supabase_client.table("storage")
        .update(storage_fields)
        .eq("id", id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data[0]


def sb_select_storage(id: str, supabase_client: Client):
    data = supabase_client.table("storage").select("*").eq("id", id).execute().data
    if len(data) == 0:
        return None
    return data[0]


def sb_select_storage_by_root(root: str, supabase_client: Client):
    data = supabase_client.table("storage").select("*").eq("root", root).execute().data
    if len(data) == 0:
        return None
    return data[0]


def sb_delete_storage(id: str, supabase_client: Client):
    data = supabase_client.table("storage").delete().eq("id", id).execute().data
    if len(data) == 0:
        return None
    return data[0]
