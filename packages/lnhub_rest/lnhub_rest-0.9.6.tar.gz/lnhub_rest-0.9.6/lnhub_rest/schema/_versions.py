from datetime import datetime as datetime
from typing import Optional

from sqlmodel import Field

from ._core import SQLModel
from ._timestamps import CreatedAt
from ._users import CreatedBy


class version_cbwk(SQLModel, table=True):  # type: ignore
    """lnhub_rest.schema version deployed in hub instance."""

    v: Optional[str] = Field(primary_key=True)
    """Python package version of `lnschema_core`."""
    migration: Optional[str] = None
    """Migration script reference of the latest migration leading up to the Python package version."""  # noqa
    breaks_lndb: bool
    """Indicates whether the migration breaks the lndb client library."""
    user_id: str = CreatedBy
    """Link to :class:`~lnschema_core.User`."""
    created_at: datetime = CreatedAt
    """Time of creation."""


class migration_cbwk(SQLModel, table=True):  # type: ignore
    """Latest migration.

    This stores the reference to the latest migration script deployed.
    """

    version_num: Optional[str] = Field(primary_key=True)
    """Reference to the last-run migration script."""
