# models/player.py

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from model.game import Game

from model.person import Person
from model.role import Role


class Player:
    """
    Represents a player in the game.
    """

    def __init__(self, person: Person, role: Role = None):
        self.person = person
        self.role = role

    def to_dict(self, game: 'Game') -> Dict[str, Any]:
        """
        Serializes the player to a dictionary.
        """
        return {
            "person": self.person.to_dict(),
            "role": self.role.to_dict(game) if self.role else None
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Player':
        """
        Deserializes a player from a dictionary.
        """
        person = Person.from_json(data["person"])
        # Role assignment is handled separately
        return cls(person=person)

    def __repr__(self):
        return f"Player(person={self.person.name}, role={self.role})"
