"""
Class representing a role
"""

import enum
from typing import Tuple


class Allegiance(enum.Enum):
    GOOD = "Good"
    BAD = "Bad"


ALLOWABLE_ALLEGIANCE_COUNTS = {
    5: {Allegiance.GOOD: 3, Allegiance.BAD: 2},
    6: {Allegiance.GOOD: 4, Allegiance.BAD: 2},
    7: {Allegiance.GOOD: 4, Allegiance.BAD: 3},
    8: {Allegiance.GOOD: 5, Allegiance.BAD: 3},
    9: {Allegiance.GOOD: 6, Allegiance.BAD: 3},
    10: {Allegiance.GOOD: 6, Allegiance.BAD: 4},
}


class Role:
    """
    Class representing a role

    Attributes:
      name (str): The name of the role
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def to_dict(self, game):
        """
        Returns a dictionary representation of the role
        """
        return {
            "name": self.name,
            "allegiance": self.allegiance().value,
            "description": self.description(),
            "information": self.information(game),
        }

    @classmethod
    def from_json(cls, data):
        """
        Updates the role from a dictionary representation
        """
        name = data["name"]
        role_class = globals()[name]
        return role_class()

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        raise NotImplementedError("ensure_constraints not implemented")

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        raise NotImplementedError("allegiance not implemented")

    def description(self):
        """
        Returns a description of the role
        """
        raise NotImplementedError("description not implemented")

    def information(self, game):
        """
        Returns information about the role
        """
        raise NotImplementedError("information not implemented")

    @classmethod
    def get_allegiance_counts(cls, roles):
        """
        Returns the number of good and bad roles in the list of roles
        """
        print("ROLES", roles)
        good_count = 0
        bad_count = 0
        for role in roles:
            if role.allegiance() == Allegiance.GOOD:
                good_count += 1
            elif role.allegiance() == Allegiance.BAD:
                bad_count += 1
        return good_count, bad_count

    @classmethod
    def get_allowable_allegiance_counts(cls, current_roles, player_count):
        """
        Returns the allowable number of good and bad roles for the given player count
        """
        allowable_allegiance_counts = ALLOWABLE_ALLEGIANCE_COUNTS[player_count]
        allowable_good_count = allowable_allegiance_counts[Allegiance.GOOD]
        allowable_bad_count = allowable_allegiance_counts[Allegiance.BAD]

        if player_count == 9 and Merlin in current_roles:
            allowable_good_count -= 1
            allowable_bad_count += 1

        return allowable_good_count, allowable_bad_count


# Good Roles


class Merlin(Role):
    """
    Class representing the Merlin role
    """

    def __init__(self):
        super().__init__("Merlin")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.

        In a 9 player game, there must be 3 or 4 bad roles. Exactly 3 if merlin is included, exactly 4 if merlin is not included.
        We can add Merlin, unless it would exceed the number of allowable good roles
        """
        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )
        # Adjust allowable good count for 9 player game, since if we add Merlin,
        # we must add an additional bad role and remove a good role
        if player_count == 9:
            allowable_good_count -= 1

        if good_count + 1 > allowable_good_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return "Merlin is a good player who knows who the bad players are."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        players_merlin_sees = list(
            filter(
                lambda player: player.role.allegiance() == Allegiance.BAD
                or type(player.role) is Lancelot,
                players,
            )
        )
        return [
            "{} is Evil.".format(player.person.name)
            for player in players_merlin_sees
            if type(player.role) is not Mordred
        ]


class Percival(Role):
    """
    Class representing the Percival role
    """

    def __init__(self):
        super().__init__("Percival")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if good_count + 1 > allowable_good_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return "Percival is a good player who knows who Merlin and Morgana are."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        players_merlin_morgana = list(
            filter(
                lambda player: type(player.role) is Merlin
                or type(player.role) is Morgana,
                players,
            )
        )
        return [
            "{} is Merlin or Morgana.".format(player.person.name)
            for player in players_merlin_morgana
        ]


class Lancelot(Role):
    """
    Class representing the Lancelot role
    """

    def __init__(self):
        super().__init__("Lancelot")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if good_count + 1 > allowable_good_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return "Lancelot is a good player who can play Reversal cards. They are seen as Evil by Merlin."

    def information(self, game):
        """
        Returns information about the role
        """
        return []


class Arthur(Role):
    """
    Class representing the Arthur role
    """

    def __init__(self):
        super().__init__("Arthur")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        if player_count < 7:
            return False, []

        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if good_count + 1 > allowable_good_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return "Arthur is a good player who knows which good roles are in the game."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        good_players = list(
            filter(
                lambda player: player.role.allegiance() == Allegiance.GOOD
                and type(player.role) is not self.__class__,
                players,
            )
        )
        return ["{}".format(player.role) for player in good_players]


class Titania(Role):
    """
    Class representing the Titania role
    """

    def __init__(self):
        super().__init__("Titania")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        if player_count < 7:
            return False, []

        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if good_count + 1 > allowable_good_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return (
            "Titania is a good player who appears evil to all players with evil roles."
        )

    def information(self, game):
        """
        Returns information about the role
        """
        return []


class Iseult(Role):
    """
    Class representing the Iseult role
    """

    def __init__(self):
        super().__init__("Iseult")
        self.required_roles = [Tristan]

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if good_count + 1 + len(self.required_roles) > allowable_good_count:
            return False, []

        return True, self.required_roles

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return "Iseult is a good player who sees Tristan."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        return [
            "{} is Tristan.".format(player.person.name)
            for player in players
            if type(player.role) is Tristan
        ]


class Tristan(Role):
    """
    Class representing the Tristan role
    """

    def __init__(self):
        super().__init__("Tristan")
        self.required_roles = [Iseult]

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        good_count, _ = Role.get_allegiance_counts(current_roles)
        allowable_good_count, _ = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if good_count + 1 + len(self.required_roles) > allowable_good_count:
            return False, []

        return True, self.required_roles

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.GOOD

    def description(self):
        """
        Returns a description of the role
        """
        return "Tristan is a good player who sees Iseult."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        return [
            "{} is Iseult.".format(player.person.name)
            for player in players
            if type(player.role) is Iseult
        ]


# Bad Roles
class Mordred(Role):
    """
    Class representing the Mordred role
    """

    def __init__(self):
        super().__init__("Mordred")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        _, bad_count = Role.get_allegiance_counts(current_roles)
        _, allowable_bad_count = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if bad_count + 1 > allowable_bad_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.BAD

    def description(self):
        """
        Returns a description of the role
        """
        return "Mordred is a bad player who is hidden from Merlin."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        other_evils = list(
            filter(
                lambda player: (player.role.allegiance() == Allegiance.BAD
                and type(player.role) is not Colgrevance)
                or type(player.role) is Titania,
                players,
            )
        )
        return [
            "{} is Evil".format(player.person.name)
            for player in other_evils
            if type(player.role) is not self.__class__
        ]


class Morgana(Role):
    """
    Class representing the Morgana role
    """

    def __init__(self):
        super().__init__("Morgana")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        _, bad_count = Role.get_allegiance_counts(current_roles)
        _, allowable_bad_count = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if bad_count + 1 > allowable_bad_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.BAD

    def description(self):
        """
        Returns a description of the role
        """
        return "Morgana is a bad player who appears as Merlin to Percival."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        other_evils = list(
            filter(
                lambda player: (player.role.allegiance() == Allegiance.BAD
                and type(player.role) is not Colgrevance)
                or type(player.role) is Titania,
                players
            )
        )
        return [
            "{} is Evil".format(player.person.name)
            for player in other_evils
            if type(player.role) is not self.__class__
        ]


class Maleagant(Role):
    """
    Class representing the Maleagant role
    """

    def __init__(self):
        super().__init__("Maleagant")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        _, bad_count = Role.get_allegiance_counts(current_roles)
        _, allowable_bad_count = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if bad_count + 1 > allowable_bad_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.BAD

    def description(self):
        """
        Returns a description of the role
        """
        return "Maleagant is a bad player who can play Reversal cards."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        other_evils = list(
            filter(
                lambda player: (player.role.allegiance() == Allegiance.BAD
                and type(player.role) is not Colgrevance)
                or type(player.role) is Titania,
                players
            )
        )
        return [
            "{} is Evil".format(player.person.name)
            for player in other_evils
            if type(player.role) is not self.__class__
        ]


class Agravain(Role):
    """
    Class representing the Agravain role
    """

    def __init__(self):
        super().__init__("Agravain")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        if player_count < 8:
            return False, []

        _, bad_count = Role.get_allegiance_counts(current_roles)
        _, allowable_bad_count = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if bad_count + 1 > allowable_bad_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.BAD

    def description(self):
        """
        Returns a description of the role
        """
        return "Agravain is a bad player who must play Fail cards."

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        other_evils = list(
            filter(
                lambda player: (player.role.allegiance() == Allegiance.BAD
                and type(player.role) is not Colgrevance)
                or type(player.role) is Titania,
                players
            )
        )
        return [
            "{} is Evil".format(player.person.name)
            for player in other_evils
            if type(player.role) is not self.__class__
        ]


class Colgrevance(Role):
    """
    Class representing the Colgrevance role
    """

    def __init__(self):
        super().__init__("Colgrevance")

    def ensure_constraints(
        self, current_roles, player_count
    ) -> Tuple[bool, list["Role"]]:
        """
        Ensures that the role can be added to the game.
        Returns a tuple of a boolean indicating if the role can be added and a list of roles that must be added if the role is added.
        If the list of roles is non-empty, the desired player_count is at most the current player count + the length of the list of roles.
        Otherwise, this role cannot be added to the game.
        """
        if player_count < 10:
            return False, []

        _, bad_count = Role.get_allegiance_counts(current_roles)
        _, allowable_bad_count = Role.get_allowable_allegiance_counts(
            current_roles, player_count
        )

        if bad_count + 1 > allowable_bad_count:
            return False, []

        return True, []

    def allegiance(self):
        """
        Returns the allegiance of the role (Good or Bad)
        """
        return Allegiance.BAD

    def description(self):
        """
        Returns a description of the role
        """
        return (
            "Colgrevance is a bad player who knows the roles of all other bad players."
        )

    def information(self, game):
        """
        Returns information about the role
        """
        players = game.players
        return [
            "{} is {}".format(player.person.name, player.role)
            for player in players
            if player.role.allegiance() == Allegiance.BAD
            and type(player.role) is not self.__class__
        ]


ALL_ROLES = Role.__subclasses__()
