# models/role_config.py

from typing import List, Union, Dict
from dataclasses import dataclass, field
from model.role_name import RoleName
from model.allegiance import Allegiance
from model.information_rule import InformationRule


@dataclass
class RoleConfig:
    """
    Configuration for a role.
    """
    name: RoleName
    allegiance: Allegiance
    description: str
    information_rules: List[InformationRule] = field(default_factory=list)
    min_players: int = 0
    max_players: int = 10
    required_roles: List[RoleName] = field(default_factory=list)
    disallowed_roles: List[RoleName] = field(default_factory=list)
    supported_variants: Union[List[str], str] = "ALL"
    rank_priority_map: Dict[int, int] = field(default_factory=dict)
