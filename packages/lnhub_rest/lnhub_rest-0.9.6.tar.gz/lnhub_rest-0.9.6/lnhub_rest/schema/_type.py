from enum import Enum


class instance_role(str, Enum):
    """Instance role types."""

    admin = "admin"
    write = "write"
    read = "read"


class organization_role(str, Enum):
    """Organization role types."""

    owner = "owner"
    member = "member"
