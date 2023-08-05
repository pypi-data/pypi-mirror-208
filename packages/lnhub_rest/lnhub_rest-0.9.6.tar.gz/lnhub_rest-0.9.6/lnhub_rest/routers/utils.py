from typing import Union

import jwt
from fastapi import Header

from lnhub_rest.orm._sbclient import connect_hub, connect_hub_with_auth

supabase_client = connect_hub()


def get_account_role_for_instance(instance_id: str, access_token: str):
    supabase_client = connect_hub_with_auth(access_token=access_token)
    session_payload = jwt.decode(
        access_token, algorithms="HS256", options={"verify_signature": False}
    )
    data = (
        supabase_client.table("account_instance")
        .select("role")
        .eq("account_id", session_payload["sub"])
        .eq("instance_id", instance_id)
        .execute()
        .data
    )
    return data[0]["role"] if len(data) > 0 else None


def extract_access_token(authentication: Union[str, None] = Header(default=None)):
    if authentication is not None:
        return authentication.split(" ")[1]
    return None


def get_supabase_client(access_token: Union[str, None]):
    if access_token is None:
        return connect_hub()
    else:
        return connect_hub_with_auth(access_token=access_token)
