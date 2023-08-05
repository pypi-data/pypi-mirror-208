from typing import Union

from fastapi import APIRouter, Header

from ..core.member._crud import (
    sb_delete_member,
    sb_insert_member,
    sb_select_members,
    sb_update_member,
)
from .utils import extract_access_token, get_supabase_client

router = APIRouter(prefix="/organization")


@router.get("/resources/members/{organization_id}")
def get_organization_members(
    organization_id: str,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    hub = get_supabase_client(access_token)
    try:
        members = sb_select_members(organization_id, hub)
        return members
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()


@router.post("/resources/members/{organization_id}/")
def add_member(
    organization_id: str,
    user_id: str,
    role: Union[str, None] = "member",
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    hub = get_supabase_client(access_token)
    try:
        organization_user_fields = {
            "organization_id": organization_id,
            "user_id": user_id,
            "role": role,
        }
        member = sb_insert_member(organization_user_fields, hub)
        if member is not None:
            return "success"
        else:
            return "member-not-added"
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()


@router.put("/resources/members/{organization_id}/")
def update_member(
    organization_id: str,
    user_id: str,
    role: str,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    hub = get_supabase_client(access_token)
    try:
        member = sb_update_member(organization_id, user_id, role, hub)
        if member is not None:
            return "success"
        else:
            return "member-not-updated"
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()


@router.delete("/resources/members/{organization_id}/")
def remove_member(
    organization_id: str,
    user_id: str,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    hub = get_supabase_client(access_token)
    try:
        member = sb_delete_member(organization_id, user_id, hub)
        if member is not None:
            return "success"
        else:
            return "member-not-deleted"
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()
