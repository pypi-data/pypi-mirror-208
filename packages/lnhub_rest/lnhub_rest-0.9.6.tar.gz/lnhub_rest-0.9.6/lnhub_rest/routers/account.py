from typing import Annotated, Union

from fastapi import APIRouter, Header, Query

from ..core.account._create_account import (
    create_organization_account,
    create_user_account,
)
from ..core.account._update_account import update_account as update_account_base
from .utils import extract_access_token, get_supabase_client, supabase_client

router = APIRouter(prefix="/account")


@router.post("/")
def create_account(
    handle: str,
    organization: Union[bool, None] = False,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    if organization:
        message = create_organization_account(
            handle=handle,
            _access_token=access_token,
        )
    else:
        message = create_user_account(
            handle=handle,
            _access_token=access_token,
        )
    if message is None:
        return "success"
    return message


@router.put("/")
def update_account(
    handle: Union[str, None] = None,
    name: Union[str, None] = None,
    bio: Union[str, None] = None,
    github_handle: Union[str, None] = None,
    linkedin_handle: Union[str, None] = None,
    twitter_handle: Union[str, None] = None,
    website: Union[str, None] = None,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    message = update_account_base(
        handle=handle,
        name=name,
        bio=bio,
        github_handle=github_handle,
        linkedin_handle=linkedin_handle,
        twitter_handle=twitter_handle,
        website=website,
        _access_token=access_token,
    )
    if message is None:
        return "success"
    return message


@router.get("/bulk/avatars")
def get_account_avatars(lnids: Annotated[list[str], Query()]):
    data = (
        supabase_client.table("account")
        .select("lnid, avatar_url")
        .in_("lnid", lnids)
        .execute()
        .data
    )
    return data if len(data) > 0 else []


@router.get("/avatar")
def get_account_avatar(lnid: str):
    data = (
        supabase_client.table("account")
        .select("avatar_url")
        .eq("lnid", lnid)
        .execute()
        .data
    )
    return data[0]["avatar_url"] if len(data) > 0 else None


@router.get("/{id}")
def get_account_by_id(id: str):
    data = supabase_client.table("account").select("*").eq("id", id).execute().data
    return data[0] if len(data) > 0 else None


@router.get("/handle/{handle}")
def get_account_by_handle(handle: str):
    data = (
        supabase_client.table("account").select("*").eq("handle", handle).execute().data
    )
    return data[0] if len(data) > 0 else None


@router.get("/resources/instances/{handle}")
def get_account_instances(
    handle: str,
    owner: bool = False,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    supabase_client = get_supabase_client(access_token)

    try:
        if owner:
            instances = (
                supabase_client.table("account")
                .select(
                    "instance!fk_instance_account_id_account(*, storage(root),"
                    " account!fk_instance_account_id_account(handle, id))"
                )
                .eq("handle", handle)
                .execute()
                .data[0]["instance"]
            )

            return instances
        else:
            account_instances = (
                supabase_client.table("account")
                .select(
                    "account_instance(instance(*, storage(root),"
                    " account!fk_instance_account_id_account(handle, id)))"
                )
                .eq("handle", handle)
                .execute()
                .data[0]["account_instance"]
            )
            account_instances = [entry["instance"] for entry in account_instances]

            return account_instances

    finally:
        supabase_client.auth.sign_out()


@router.get("/resources/organizations/{handle}")
def get_account_organizations(
    handle: str, authentication: Union[str, None] = Header(default=None)
):
    access_token = extract_access_token(authentication)
    supabase_client = get_supabase_client(access_token)

    try:
        user_id = get_account_by_handle(handle)["id"]
        organizations_user = (
            supabase_client.table("organization_user")
            .select("""*, account(*)""")
            .eq("user_id", user_id)
            .execute()
            .data
        )
        return organizations_user

    finally:
        supabase_client.auth.sign_out()
