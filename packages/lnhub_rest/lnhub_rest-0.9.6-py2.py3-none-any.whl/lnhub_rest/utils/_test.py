import os
import uuid
from typing import Union

import requests  # type: ignore

from lnhub_rest.core.account._crud import sb_insert_account
from lnhub_rest.core.collaborator._crud import sb_insert_collaborator
from lnhub_rest.core.instance._crud import sb_insert_instance
from lnhub_rest.core.storage._crud import sb_insert_storage
from lnhub_rest.orm._sbclient import (
    connect_hub,
    connect_hub_with_auth,
    connect_hub_with_service_role,
    get_lamin_site_base_url,
)
from lnhub_rest.utils._access_token import extract_id
from lnhub_rest.utils._id import base62


def create_test_auth():
    handle = f"lamin.ci.user.{base62(6)}"
    email = f"{handle}@gmail.com"
    password = "password"

    if "LAMIN_ENV" in os.environ and os.environ["LAMIN_ENV"] != "local":
        hub = connect_hub_with_service_role()
        generate_link_response = hub.auth.admin.generate_link(
            {
                "type": "signup",
                "email": email,
                "password": password,
                "options": {
                    "redirect_to": get_lamin_site_base_url(),
                },
            }
        )
        action_link = generate_link_response.properties.action_link
        try:
            requests.get(action_link)
        except Exception as e:  # noqa
            raise e
        auth_response = hub.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
    else:
        hub = connect_hub()
        auth_response = hub.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

    return {
        "handle": handle,
        "email": email,
        "password": password,
        "id": str(auth_response.session.user.id),
        "access_token": auth_response.session.access_token,
        "session": auth_response.session,
    }


def create_test_account(
    handle: str,
    access_token: str,
    organization: Union[bool, None] = False,
):
    hub = connect_hub_with_auth(access_token=access_token)

    account_id = extract_id(access_token)

    account = sb_insert_account(
        {
            "id": account_id,
            "lnid": base62(8),
            "handle": handle,
            "user_id": None if organization else account_id,
        },
        hub,
    )

    hub.auth.sign_out()

    return account


def create_test_instance(storage_id: str, access_token: str):
    hub = connect_hub_with_auth(access_token=access_token)

    account_id = extract_id(access_token)

    name = f"lamin.ci.instance.{base62(6)}"

    instance = sb_insert_instance(
        {
            "id": uuid.uuid4().hex,
            "account_id": account_id,
            "name": name,
            "storage_id": storage_id,
            "public": True,
        },
        hub,
    )

    hub.auth.sign_out()

    return instance


def create_test_storage(access_token: str):
    hub = connect_hub_with_auth(access_token=access_token)

    root = f"lamin.ci.storage.{base62(6)}"
    account_id = extract_id(access_token)

    storage = sb_insert_storage(
        {
            "id": uuid.uuid4().hex,
            "lnid": base62(8),
            "created_by": account_id,
            "root": root,
            "region": "us-east-1",
            "type": "s3",
        },
        hub,
    )

    hub.auth.sign_out()

    return storage


def add_test_collaborator(
    instance_id: str,
    account_id: str,
    role: str,
    access_token: str,
):
    hub = connect_hub_with_auth(access_token=access_token)

    collaborator = sb_insert_collaborator(
        {
            "instance_id": instance_id,
            "account_id": account_id,
            "role": role,
        },
        hub,
    )

    hub.auth.sign_out()

    return collaborator
