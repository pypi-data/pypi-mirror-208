from supabase.client import Client


def sb_insert_member(organization_user_fields: dict, supabase_client: Client):
    try:
        (
            supabase_client.table("organization_user")
            .insert(organization_user_fields, returning="minimal")
            .execute()
            .data
        )
    except Exception as e:
        if str(e) == str("Expecting value: line 1 column 1 (char 0)"):
            pass
        else:
            raise e
    return sb_select_member(
        organization_id=organization_user_fields["organization_id"],
        user_id=organization_user_fields["user_id"],
        supabase_client=supabase_client,
    )


def sb_select_member(organization_id: str, user_id: str, supabase_client: Client):
    data = (
        supabase_client.table("organization_user")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    else:
        return data[0]


def sb_select_members(organization_id: str, supabase_client: Client):
    data = (
        supabase_client.table("organization_user")
        .select("*")
        .eq("organization_id", organization_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    else:
        return data


def sb_update_member(
    organization_id: str, user_id: str, role: str, supabase_client: Client
):
    data = (
        supabase_client.table("organization_user")
        .update({"role": role})
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    else:
        return data[0]


def sb_delete_member(organization_id: str, user_id: str, supabase_client: Client):
    data = (
        supabase_client.table("organization_user")
        .delete()
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
        .execute()
        .data
    )
    if len(data) == 0:
        return None
    return data[0]
