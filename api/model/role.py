import random
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING, Union

from model.allegiance import Allegiance
from model.information_rule import InformationRule
from model.role_config import RoleConfig
from model.role_name import RoleName

if TYPE_CHECKING:
  from model.game import Game


ALLOWABLE_ALLEGIANCE_COUNTS = {
  5: {Allegiance.GOOD: 3, Allegiance.BAD: 2},
  6: {Allegiance.GOOD: 4, Allegiance.BAD: 2},
  7: {Allegiance.GOOD: 4, Allegiance.BAD: 3},
  8: {Allegiance.GOOD: 5, Allegiance.BAD: 3},
  9: {Allegiance.GOOD: 6, Allegiance.BAD: 3},
  10: {Allegiance.GOOD: 6, Allegiance.BAD: 4},
}

class Role:
  def __init__(
    self,
    name: RoleName,
    allegiance: Allegiance,
    description: str,
    information_rules: Optional[List[InformationRule]] = None,
    min_players: int = 0,
    max_players: int = 10,
    required_roles: Optional[List['Role']] = None,
    disallowed_roles: Optional[List['Role']] = None,
    supported_variants: Union[List[str], str] = "ALL",
    rank_priority_map: dict[int, int] = {}
  ):
    self.name = name
    self.allegiance = allegiance
    self.description = description
    self.information_rules = information_rules or []
    self.min_players = min_players
    self.max_players = max_players
    self.required_roles = required_roles or []
    self.disallowed_roles = disallowed_roles or []
    self.supported_variants = supported_variants
    self.rank_priority_map = rank_priority_map

  def __str__(self):
    return self.name.value

  def __repr__(self):
    return f"Role(name={self.name.value})"

  def to_dict(self, game: "Game") -> Dict:
    return {
      "name": self.name.value,
      "allegiance": self.allegiance.value,
      "description": self.description,
      "information": self.information(game),
    }

  @classmethod
  def from_json(cls, data: Dict) -> 'Role':
    role = next((role for role in ALL_ROLES if role.name.value == data["name"]), None)
    if role:
      return role
    raise ValueError(f"Role '{data['name']}' not found.")

  def ensure_constraints(
    self, current_roles: List['Role'], player_count: int
  ) -> Tuple[bool, List['Role']]:
    if any(role.name == self.name for role in current_roles):
      return False, []
    
    if any(role.name in self.disallowed_roles for role in current_roles):
      return False, []

    if player_count < self.min_players or player_count > self.max_players:
      return False, []

    good_count, bad_count = self.get_allegiance_counts(current_roles)
    allowable_good, allowable_bad = self.get_allowable_allegiance_counts(
      current_roles, player_count
    )

    if self.allegiance == Allegiance.GOOD:
      if good_count + 1 + len(self.required_roles) > allowable_good:
        return False, []
    elif self.allegiance == Allegiance.BAD:
      if bad_count + 1 > allowable_bad:
        return False, []

    return True, self.required_roles

  def information(self, game: "Game") -> List[str]:
    info_messages = []

    # Iterate through information rules
    for rule in self.information_rules:
      if not rule.unique:
        for player in game.players:
          role = player.role
          # Apply filter_roles
          if rule.filter_roles and role.name not in rule.filter_roles:
            continue
          # Apply condition
          if rule.condition and not rule.condition(role, game, self):
            continue
          # Format message
          message = rule.message.format(name=player.person.name, role_name=role.name.value)
          info_messages.append(message)

      # Apply unique
      if rule.unique and rule.condition(role, game, self):
        message = rule.message.format(name=player.person.name, role_name=role.name.value)
        info_messages.append(message)

    return info_messages

  def can_use_for_variant(self, variant: str) -> bool:
    if self.supported_variants == "ALL":
      return True
    return variant in self.supported_variants

  @classmethod
  def get_allegiance_counts(cls, roles: List['Role']) -> Tuple[int, int]:
    good_count = sum(1 for role in roles if role.allegiance == Allegiance.GOOD)
    bad_count = sum(1 for role in roles if role.allegiance == Allegiance.BAD)
    return good_count, bad_count

  def get_allowable_allegiance_counts(
    self, current_roles: List['Role'], player_count: int
  ) -> Tuple[int, int]:
    allowable = ALLOWABLE_ALLEGIANCE_COUNTS[player_count].copy()
    # Example condition for specific roles affecting counts
    if player_count == 9 and (
      any(role.name == RoleName.MERLIN for role in current_roles)
      or self.name == RoleName.MERLIN
    ):
      allowable[Allegiance.GOOD] -= 1
      allowable[Allegiance.BAD] += 1

    return allowable[Allegiance.GOOD], allowable[Allegiance.BAD]
  
  def priority(self, player_count: int):
    return random.randint(0, 100 + self.rank_priority_map.get(player_count, 0))


# Define all role configurations with typed references
ROLE_CONFIGS = [
  RoleConfig(
    name=RoleName.NIMUE,
    allegiance=Allegiance.GOOD,
    description=(
      "You know which Good and Evil roles are in the game, but not who has any given role.\nYou are a valid Assassination target."
    ),
    min_players=5,
    max_players=5,
    information_rules=[
      InformationRule(
        condition=lambda role, __, self_role: role.name != self_role.name,
        message="{role_name}"
      ),
    ]
  ),
  RoleConfig(
    name=RoleName.TRISTAN,
    allegiance=Allegiance.GOOD,
    description=(
      "The person you see is also Good and is aware that you are Good.\n"
      "You and Iseult are collectively a valid Assassination target."
    ),
    information_rules=[
      InformationRule(
        filter_roles=[RoleName.ISEULT],
        message="{name} is Iseult."
      )
    ],
    required_roles=[RoleName.ISEULT],
    disallowed_roles=[RoleName.OLDER_SIBLING],
    rank_priority_map={5: -10, 6: -10, 7: -10, 8: -10, 9: -20, 10: -10},
  ),
  RoleConfig(
    name=RoleName.ISEULT,
    allegiance=Allegiance.GOOD,
    description=(
      "The person you see is also Good and is aware that you are Good.\n"
      "You and Tristan are collectively a valid Assassination target.\n"
      "You appear to the Jealous Ex."
    ),
    information_rules=[
      InformationRule(
        filter_roles=[RoleName.TRISTAN],
        message="{name} is Tristan."
      )
    ],
    required_roles=[RoleName.TRISTAN],
    disallowed_roles=[RoleName.OLDER_SIBLING],
    rank_priority_map={5: -10, 6: -10, 7: -10, 8: -10, 9: -20, 10: -10},
  ),
  RoleConfig(
    name=RoleName.MERLIN,
    allegiance=Allegiance.GOOD,
    description=(
      "You know which people have Evil roles, but not who has any specific role.\n"
      "You are a valid Assassination target."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, __:
          (role.allegiance == Allegiance.BAD and role.name != RoleName.MORDRED) or role.name == RoleName.LANCELOT,
        message="{name} is Evil."
      ),
    ],
    rank_priority_map={9: 40}
  ),
  RoleConfig(
    name=RoleName.PERCIVAL,
    allegiance=Allegiance.GOOD,
    description=(
      "You know which people have the Merlin or Morgana roles, but not specifically who has each."
    ),
    information_rules=[
      InformationRule(
        filter_roles=[RoleName.MERLIN, RoleName.MORGANA],
        message="{name} is Merlin or Morgana."
      )
    ],
  ),
  RoleConfig(
    name=RoleName.LANCELOT,
    allegiance=Allegiance.GOOD,
    description=(
      "You may play Reversal cards while on missions.\nYou appear Evil to Merlin."
    ),
  ),
  RoleConfig(
    name=RoleName.ARTHUR,
    allegiance=Allegiance.GOOD,
    description=(
      "You know which Good roles are in the game, but not who has any given role.\n"
      "If two missions have Failed, and less than two missions have Succeeded, you may declare as Arthur.\n"
      "After declaring, your vote on team proposals is counted twice, but you are unable to be on mission teams until the 5th mission.\n"
      "After declaring, you are immune to any effect that can forcibly change your vote."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          role.allegiance == Allegiance.GOOD and role.name != self_role.name,
        message="{role_name}"
      )
    ],
    min_players=7,
  ),
  RoleConfig(
    name=RoleName.TITANIA,
    allegiance=Allegiance.GOOD,
    description=(
      "You appear as Evil to all players with Evil roles (except Colgrevance)."
    ),
    min_players=7,
  ),
  RoleConfig(
    name=RoleName.MORDRED,
    allegiance=Allegiance.BAD,
    description=(
      "You are hidden from all Good Information roles.\n"
      "Like other Evil characters, you know who else is Evil."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          (role.allegiance == Allegiance.BAD or role.name == RoleName.TITANIA)
          and role.name != self_role.name,
        message="{name} is Evil."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.TITANIA for role in game.get_roles()),
        message="Titania infiltrated your ranks."
      )
    ],
    rank_priority_map={5: 30, 6: 30, 7: 30, 8: 30, 9: 30, 10: 30},
  ),
  RoleConfig(
    name=RoleName.MORGANA,
    allegiance=Allegiance.BAD,
    description=(
      "You appear like Merlin to Percival.\n"
      "Like other Evil characters, you know who else is Evil."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          (role.allegiance == Allegiance.BAD or role.name == RoleName.TITANIA)
          and role.name != self_role.name,
        message="{name} is Evil."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.TITANIA for role in game.get_roles()),
        message="Titania infiltrated your ranks."
      )
    ],
  ),
  RoleConfig(
    name=RoleName.MAELAGANT,
    allegiance=Allegiance.BAD,
    description=(
      "You may play Reversal cards while on missions.\n"
      "Like other Evil characters, you know who else is Evil."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          (role.allegiance == Allegiance.BAD or role.name == RoleName.TITANIA)
          and role.name != self_role.name,
        message="{name} is Evil."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.TITANIA for role in game.get_roles()),
        message="Titania infiltrated your ranks."
      )
    ],
  ),
  RoleConfig(
    name=RoleName.AGRAVAINE,
    allegiance=Allegiance.BAD,
    description=(
      "You must play Fail cards while on missions.\n"
      "If you are on a mission that Succeeds, you may declare as Agravaine to cause it to Fail instead.\n"
      "Like other Evil characters, you know who else is Evil."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          (role.allegiance == Allegiance.BAD or role.name == RoleName.TITANIA)
          and role.name != self_role.name,
        message="{name} is Evil."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.TITANIA for role in game.get_roles()),
        message="Titania infiltrated your ranks."
      )
    ],
    min_players=8,
  ),
  RoleConfig(
    name=RoleName.COLGREVANCE,
    allegiance=Allegiance.BAD,
    description=(
      "You know not only who else is Evil, but what role each other Evil player possesses.\n"
      "Evil players know that there is a Colgrevance, but do not know that it is you."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          role.allegiance == Allegiance.BAD and role.name != self_role.name,
        message="{name} is {role_name}."
      ),
    ],
    min_players=10,
  ),
  RoleConfig(
    name=RoleName.JEALOUS_EX,
    allegiance=Allegiance.BAD,
    description=(
      "You see either Iseult (if there are two lovers) or the Older Sibling (if there are no lovers)."
    ),
    information_rules=[
      InformationRule(
        filter_roles=[RoleName.ISEULT, RoleName.OLDER_SIBLING],
        message="{name} is Iseult or the Older Sibling."
      ),
      InformationRule(
        condition=lambda role, _, self_role:
          (role.allegiance == Allegiance.BAD or role.name == RoleName.TITANIA)
          and role.name != self_role.name,
        message="{name} is Evil."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.TITANIA for role in game.get_roles()),
        message="Titania infiltrated your ranks."
      )
    ],
    supported_variants=["jealousy", "esoteric"],
  ),
  RoleConfig(
    name=RoleName.OLDER_SIBLING,
    allegiance=Allegiance.GOOD,
    description=(
      "You appear to the Jealous Ex as Iseult. You know there are no lovers in this game."
    ),
    disallowed_roles=[RoleName.TRISTAN, RoleName.ISEULT],
    supported_variants=["jealousy", "esoteric"],
  ),
  RoleConfig(
    name=RoleName.UNICORN,
    allegiance=Allegiance.GOOD,
    description=(
      "You are a Good role that sees the lovers (Tristan and Iseult, if they are in the game) or the Older Sibling (if they are in the game), "
      "and Mordred (if they are in the game). You do not specifically know who are each.\n"
      "You are a valid Assassination target."
    ),
    information_rules=[
      InformationRule(
        filter_roles=[RoleName.TRISTAN, RoleName.ISEULT, RoleName.OLDER_SIBLING, RoleName.MORDRED],
        message="{name} is Tristan or Iseult or Older Sibling or Mordred."
      )
    ],
    supported_variants=["esoteric"],
  ),
  RoleConfig(
    name=RoleName.POLITICIAN,
    allegiance=Allegiance.BAD,
    description=(
      "You are an Evil role that can play Cancelation cards while on missions. You are aware of the presence of Lancelot, but not who they are. "
      "You know who Maelagant is, if they are in play.\n"
      "A Cancelation card removes all Reversal cards."
    ),
    information_rules=[
      InformationRule(
        condition=lambda role, _, self_role:
          (role.allegiance == Allegiance.BAD or role.name == RoleName.TITANIA)
          and role.name != self_role.name,
        message="{name} is Evil."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.LANCELOT for role in game.get_roles()),
        message="Lancelot is in the game."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: not any(role.name == RoleName.LANCELOT for role in game.get_roles()),
        message="Lancelot is NOT in the game."
      ),
      InformationRule(
        condition=lambda role, _, __: role.name == RoleName.MAELAGANT,
        message="{name} is Maelagant."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: not any(role.name == RoleName.MAELAGANT for role in game.get_roles()),
        message="Maelagant is NOT in the game."
      ),
      InformationRule(
        unique=True,
        condition=lambda _, game, __: any(role.name == RoleName.TITANIA for role in game.get_roles()),
        message="Titania infiltrated your ranks."
      )
    ],
    supported_variants=["esoteric"],
  ),
]


def create_roles(configs: List[RoleConfig]) -> List[Role]:
  roles: list[Role] = []
  name_to_role: dict[RoleName, Role] = {}

  # First pass: Create Role instances without required_roles
  for config in configs:
    role = Role(
      name=config.name,
      allegiance=config.allegiance,
      description=config.description,
      information_rules=config.information_rules,
      min_players=config.min_players,
      max_players=config.max_players,
      disallowed_roles=config.disallowed_roles,
      supported_variants=config.supported_variants,
      rank_priority_map=config.rank_priority_map
    )
    roles.append(role)
    name_to_role[role.name] = role

  # Second pass: Assign required_roles
  for config in configs:
    role = name_to_role[config.name]
    required_role_names = config.required_roles
    role.required_roles = [name_to_role[r_name] for r_name in required_role_names]

  return roles


# Instantiate all roles
ALL_ROLES: List[Role] = create_roles(ROLE_CONFIGS)
