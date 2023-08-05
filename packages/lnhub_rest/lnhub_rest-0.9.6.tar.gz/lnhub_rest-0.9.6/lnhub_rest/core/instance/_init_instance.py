"""Initializing an instance.

This functionality will at first only be accessible through Python API client & CLI.

We might also enable it from the UI.
"""
from typing import Mapping, Optional
from uuid import UUID, uuid4

from postgrest.exceptions import APIError

from lnhub_rest import check_breaks_lndb_and_error
from lnhub_rest._assets import schemas as known_schema_names
from lnhub_rest.core.account._crud import sb_select_account_by_handle
from lnhub_rest.core.collaborator._crud import sb_insert_collaborator
from lnhub_rest.core.instance._crud import (
    sb_insert_instance,
    sb_select_instance_by_name,
)
from lnhub_rest.core.storage import add_storage
from lnhub_rest.orm._sbclient import connect_hub_with_auth


def init_instance(
    *,
    owner: str,  # owner handle
    name: str,  # instance name
    storage: str,  # storage location on cloud
    db: Optional[str] = None,  # str has to be postgresdsn (use pydantic in the future)
    schema: Optional[str] = None,  # comma-separated list of schema names
    description: Optional[str] = None,
    public: Optional[bool] = None,
    # replace with token-based approach!
    _email: Optional[str] = None,
    _password: Optional[str] = None,
    _access_token: Optional[str] = None,
) -> Optional[str]:
    hub = connect_hub_with_auth(
        email=_email, password=_password, access_token=_access_token
    )
    check_breaks_lndb_and_error(hub)  # assumes that only called from within lndb
    try:
        # validate input arguments
        schema_str = validate_schema_arg(schema)
        # storage is validated in add_storage
        validate_db_arg(db)

        # get account
        account = sb_select_account_by_handle(owner, hub)
        if account is None:
            return "account-not-exists"

        # get storage and add if not yet there
        storage_root = storage.rstrip("/")  # current fix because of upath migration
        storage_id, message = add_storage(
            storage_root, account_handle=account["handle"], _access_token=_access_token
        )
        if message is not None:
            return message
        assert storage_id is not None

        instance = sb_select_instance_by_name(account["id"], name, hub)
        if instance is not None:
            return "instance-exists-already"

        validate_unique_sqlite(
            hub=hub, db=db, storage_id=storage_id, name=name, account=account
        )

        instance_id = uuid4().hex

        sb_insert_instance(
            {
                "id": instance_id,
                "account_id": account["id"],
                "name": name,
                "storage_id": storage_id,
                "db": db,
                "schema_str": schema_str,
                "public": False if public is None else public,
                "description": description,
            },
            hub,
        )

        sb_insert_collaborator(
            {
                "instance_id": instance_id,
                "account_id": account["id"],
                "role": "admin",
            },
            hub,
        )

        # upon successful insert of a new row in the instance table
        # (and all associated tables), return None
        # clients test for this return value, hence, don't change it
        return None
    except APIError as api_error:
        uq_instance_db_error = (
            'duplicate key value violates unique constraint "uq_instance_db"'
        )
        if api_error.message == uq_instance_db_error:
            return "db-already-exists"
        raise api_error
    except Exception as e:
        raise e
    finally:
        hub.auth.sign_out()


def validate_schema_arg(schema: Optional[str] = None) -> str:
    if schema is None or schema == "":
        return ""
    validated_schema = []
    to_be_validated = [s.strip() for s in schema.split(",")]
    for name in known_schema_names:
        if name in to_be_validated:
            validated_schema.append(name)
            to_be_validated.remove(name)
    if len(to_be_validated) != 0:
        raise ValueError(f"Unkown schema module name(s): {to_be_validated}")
    return ",".join(validated_schema)


def validate_db_arg(db: Optional[str]) -> None:
    if db is not None:
        if db.startswith("postgres") and not db.startswith("postgresql"):
            raise ValueError(
                "Please follow the SQLAlchemy convention of prefixing the connection"
                " string with 'postgresql://' instead of 'postgres://'"
            )
        if not db.startswith("postgresql"):
            raise ValueError("Only postgres connection strings are allowed.")
        if not len(db.split("://")) == 2:
            raise ValueError("Your postgres URI does not contain '://'")
        remainder = db.split("://")[1]
        if not len(remainder.split("/")) == 2:
            raise ValueError("Your postgres URI does not end with a database '/dbname'")


def validate_unique_sqlite(
    *, hub, db: Optional[str], storage_id: UUID, name: str, account: Mapping
) -> None:
    # if a remote sqlite instance, make sure there is no other instance
    # that has the same name and storage location
    if db is None:  # remote sqlite instance
        instances = (
            hub.table("instance")
            .select("*")
            .eq("storage_id", storage_id)
            .eq("name", name)
            .execute()
            .data
        )
        if len(instances) > 0:
            # retrieve account owning the first instance
            accounts = (
                hub.table("account")
                .select("*")
                .eq("id", instances[0]["account_id"])
                .execute()
                .data
            )
            raise RuntimeError(
                "\nThere is already an sqlite instance with the same name and storage"
                f" location from account {accounts[0]['handle']}\nTwo sqlite instances"
                " with the same name and the same storage cannot exist\nFix: "
                f"Choose another name or load instance {accounts[0]['handle']}/{name}\n"
            )
