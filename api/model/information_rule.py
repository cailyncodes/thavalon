# models/information_rule.py

from typing import Callable, List, TYPE_CHECKING, Optional
from dataclasses import dataclass, field
from model.role_name import RoleName

if TYPE_CHECKING:
    from model.role import Role
    from model.game import Game


@dataclass
class InformationRule:
    """
    Represents an information rule for a role.
    """
    condition: Optional[Callable[['Role', 'Game', 'Role'], bool]] = None
    filter_roles: Optional[List[RoleName]] = None
    unique: bool = False
    message: str = ""
    # The message can include placeholders like {name} or {role_name}
