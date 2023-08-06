"""This module defines the groups in Qtile"""

from enum import Enum
from libqtile.config import Group


class GroupName(Enum):
    """Enumerated group names"""

    WEB = "a"
    CHAT = "s"
    TERM = "d"
    DEV = "f"
    NULL = "g"
    TMP = "z"
    CALL = "x"
    SANDBOX1 = "c"
    SANDBOX2 = "v"
    SANDBOX3 = "b"


groups = [
    Group(f"{group.value}: {group.name}") for ix, group in enumerate(list(GroupName))
]
