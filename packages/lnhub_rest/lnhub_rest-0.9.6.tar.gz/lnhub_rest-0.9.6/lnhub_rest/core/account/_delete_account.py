from typing import Optional, Union

from lnhub_rest.core.account._crud import sb_delete_account, sb_select_account_by_handle
from lnhub_rest.core.collaborator._crud import sb_delete_collaborator_from_all_instances
from lnhub_rest.orm._sbclient import connect_hub_with_auth


def delete_account(
    handle: str,  # owner handle
    _access_token: Optional[str] = None,
) -> Union[None, str]:
    hub = connect_hub_with_auth(access_token=_access_token)
    try:
        account = sb_select_account_by_handle(handle, hub)
        sb_delete_collaborator_from_all_instances(account["id"], hub)
        sb_delete_account(handle, hub)
        return None
    except Exception as e:
        return str(e)
    finally:
        hub.auth.sign_out()
