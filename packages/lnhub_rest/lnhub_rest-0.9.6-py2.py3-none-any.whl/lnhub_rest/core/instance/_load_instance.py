from typing import Optional, Tuple, Union

from lnhub_rest import check_breaks_lndb_and_error
from lnhub_rest.core.account._crud import sb_select_account_by_handle
from lnhub_rest.core.instance._crud import sb_select_instance_by_name
from lnhub_rest.core.storage._crud import sb_select_storage
from lnhub_rest.orm._sbclient import connect_hub_with_auth
from lnhub_rest.schema import Instance, Storage


def load_instance(
    *,
    owner: str,  # owner handle
    name: str,  # instance name
    _email: Optional[str] = None,
    _password: Optional[str] = None,
    _access_token: Optional[str] = None,
) -> Union[Tuple[Instance, Storage], str]:
    hub = connect_hub_with_auth(
        email=_email, password=_password, access_token=_access_token
    )
    try:
        check_breaks_lndb_and_error(hub)  # assumes that only called from within lndb
        # get account
        account = sb_select_account_by_handle(owner, hub)
        if account is None:
            return "account-not-exists"

        instance = sb_select_instance_by_name(account["id"], name, hub)
        if instance is None:
            return "instance-not-reachable"
        instance = Instance(**instance)

        # get default storage
        storage = sb_select_storage(instance.storage_id, hub)
        if storage is None:
            return "storage-does-not-exist-on-hub"
        storage = Storage(**storage)

        return instance, storage
    except Exception:
        return "loading-instance-failed"
    finally:
        hub.auth.sign_out()
