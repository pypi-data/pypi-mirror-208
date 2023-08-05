import os
from pathlib import Path
from typing import Optional, Tuple
from uuid import UUID, uuid4

from lnhub_rest import check_breaks_lndb_and_error
from lnhub_rest.core.storage._crud import sb_insert_storage, sb_select_storage_by_root
from lnhub_rest.orm._sbclient import connect_hub_with_auth
from lnhub_rest.utils._id import base62


def add_storage(
    root: str, account_handle: str, _access_token: Optional[str] = None
) -> Tuple[Optional[UUID], Optional[str]]:
    from botocore.exceptions import ClientError

    from lnhub_rest.core.account._crud import sb_select_account_by_handle

    hub = connect_hub_with_auth(access_token=_access_token)
    try:
        check_breaks_lndb_and_error(hub)  # assumes that only called from within lndb
        validate_storage_root_arg(root)
        # get account
        account = sb_select_account_by_handle(account_handle, hub)

        # check if storage exists already
        storage = sb_select_storage_by_root(root, hub)
        if storage is not None:
            return storage["id"], None

        # add storage
        if "LNHUB_NOT_USE_BOTO3" in os.environ:
            storage_region = None
        else:
            storage_region = get_storage_region(root)
        storage_type = get_storage_type(root)
        storage = sb_insert_storage(
            {
                "id": uuid4().hex,
                "lnid": base62(8),
                "created_by": account["id"],
                "root": root,
                "region": storage_region,
                "type": storage_type,
            },
            hub,
        )
        assert storage is not None

        return storage["id"], None
    except ClientError as exception:
        if exception.response["Error"]["Code"] == "NoSuchBucket":
            return None, "bucket-does-not-exists"
        else:
            return None, exception.response["Error"]["Message"]
    finally:
        hub.auth.sign_out()


def validate_storage_root_arg(storage_root: str) -> None:
    if storage_root.endswith("/"):
        raise ValueError("Pass settings.storage.root_as_str rather than path")
    if storage_root.startswith(("gs://", "s3://")):
        return None
    else:  # local path
        try:
            _ = Path(storage_root)
            return None
        except Exception:
            raise ValueError(
                "`storage` is neither a valid local, a Google Cloud nor an S3 path."
            )


def get_storage_region(storage_root: str) -> Optional[str]:
    storage_root_str = str(storage_root)
    storage_region = None

    if storage_root_str.startswith("s3://"):
        import boto3

        response = boto3.client("s3").get_bucket_location(
            Bucket=storage_root_str.replace("s3://", "")
        )
        # returns `None` for us-east-1
        # returns a string like "eu-central-1" etc. for all other regions
        storage_region = response["LocationConstraint"]
        if storage_region is None:
            storage_region = "us-east-1"

    return storage_region


def get_storage_type(storage_root: str):
    if str(storage_root).startswith("s3://"):
        return "s3"
    elif str(storage_root).startswith("gs://"):
        return "gs"
    else:
        return "local"
