from typing import Union
from uuid import uuid4

from postgrest.exceptions import APIError

from lnhub_rest.core.account._crud import sb_insert_account
from lnhub_rest.core.member._crud import sb_insert_member
from lnhub_rest.orm._sbclient import connect_hub_with_auth
from lnhub_rest.utils._access_token import extract_id
from lnhub_rest.utils._id import base62


def create_user_account(
    _access_token: str,
    handle: str,
) -> Union[None, str]:
    hub = connect_hub_with_auth(access_token=_access_token)
    try:
        lnid = base62(8)
        id = extract_id(_access_token)

        account = sb_insert_account(
            {
                "id": id,
                "user_id": id,
                "lnid": lnid,
                "handle": handle,
            },
            hub,
        )
        assert account is not None

        return None
    except APIError as api_error:
        # allowed errors
        message = api_error.message
        error1 = 'duplicate key value violates unique constraint "pk_account"'
        error2 = 'duplicate key value violates unique constraint "usermeta_pkey"'
        if message == error1 or message == error2:
            return "handle-exists-already"
        raise api_error
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()


def create_organization_account(handle: str, _access_token: str) -> Union[None, str]:
    hub = connect_hub_with_auth(access_token=_access_token)
    try:
        lnid = base62(8)

        organization = sb_insert_account(
            {
                "id": uuid4().hex,
                "user_id": None,
                "lnid": lnid,
                "handle": handle,
            },
            hub,
        )
        assert organization is not None

        user_id = extract_id(_access_token)
        member = sb_insert_member(
            {
                "organization_id": organization["id"],
                "user_id": user_id,
                "role": "owner",
            },
            hub,
        )
        assert member is not None

        return None
    except APIError as api_error:
        # allowed errors
        message = api_error.message
        error1 = 'duplicate key value violates unique constraint "pk_account"'
        error2 = 'duplicate key value violates unique constraint "usermeta_pkey"'
        if message == error1 or message == error2:
            return "handle-exists-already"
        raise api_error
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()
