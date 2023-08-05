from typing import Optional, Union

from lnhub_rest.core.account._crud import sb_update_account
from lnhub_rest.orm._sbclient import connect_hub_with_auth
from lnhub_rest.utils._access_token import extract_id
from lnhub_rest.utils._query import filter_null_from_dict


def update_account(
    _access_token: str,
    handle: Optional[str] = None,
    name: Optional[str] = None,
    bio: Optional[str] = None,
    github_handle: Optional[str] = None,
    linkedin_handle: Optional[str] = None,
    twitter_handle: Optional[str] = None,
    website: Optional[str] = None,
) -> Union[None, str]:
    hub = connect_hub_with_auth(access_token=_access_token)
    try:
        id = extract_id(_access_token)

        data = hub.table("account").select("*").eq("id", id).execute().data
        if len(data) == 0:
            return "account-not-exists"

        fields = filter_null_from_dict(
            {
                "id": id,
                "handle": handle,
                "name": name,
                "bio": bio,
                "github_handle": github_handle,
                "linkedin_handle": linkedin_handle,
                "twitter_handle": twitter_handle,
                "website": website,
            }
        )

        account = sb_update_account(id, fields, hub)
        assert account is not None

        return None
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()
