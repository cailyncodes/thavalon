"""
Class representing a player
"""

from .person import Person
from .role import Role


class Player:
    """
    Class representing a player

    Attributes:
      person (Person): The person that is the player
      role (Role): The role of the player
    """

    def __init__(self, person, role):
        self.person = person
        self.role = role

    def __str__(self):
        return f"{self.person.name} is a {self.role.name}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self, game):
        """
        Returns a dictionary representation of the player
        """
        return {
            "person": self.person.to_dict(),
            "role": self.role.to_dict(game),
        }

    @classmethod
    def from_json(cls, data):
        """
        Updates the player from a dictionary representation
        """
        person = Person.from_json(data["person"])
        role = Role.from_json(data["role"])
        return cls(person, role)
