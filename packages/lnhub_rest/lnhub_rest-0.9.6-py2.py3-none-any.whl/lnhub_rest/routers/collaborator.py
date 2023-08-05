from typing import Union

from fastapi import APIRouter, Header

from lnhub_rest.core.collaborator._crud import (
    sb_delete_collaborator,
    sb_select_collaborator,
    sb_update_collaborator,
)

from .instance import get_instance_by_name
from .utils import extract_access_token, get_supabase_client

router = APIRouter(prefix="/instance/collaborator")


@router.get("/{account_handle}/{name}")
def is_collaborator(
    instance_id: str,
    account_id: str,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    supabase_client = get_supabase_client(access_token)

    try:
        collaborator = sb_select_collaborator(instance_id, account_id, supabase_client)
        if collaborator is None:
            return False
        else:
            return True
    finally:
        supabase_client.auth.sign_out()


@router.put("/{account_handle}/{name}")
def update_collaborator(
    account_handle: str,
    name: str,
    account_id: str,
    role: str,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    supabase_client = get_supabase_client(access_token)

    try:
        instance_id = get_instance_by_name(account_handle, name, authentication)[
            "instance"
        ]["id"]
        collaborator = sb_update_collaborator(
            instance_id, account_id, role, supabase_client
        )
        if collaborator is None:
            return "update-failed"
        else:
            return collaborator
    finally:
        supabase_client.auth.sign_out()


@router.delete("/{account_handle}/{name}")
def delete_collaborator(
    account_handle: str,
    name: str,
    account_id: str,
    authentication: Union[str, None] = Header(default=None),
):
    access_token = extract_access_token(authentication)
    supabase_client = get_supabase_client(access_token)

    try:
        instance_id = get_instance_by_name(account_handle, name, authentication)[
            "instance"
        ]["id"]
        collaborator = sb_delete_collaborator(instance_id, account_id, supabase_client)
        if collaborator is None:
            return "delete-failed"
        else:
            return collaborator
    finally:
        supabase_client.auth.sign_out()
