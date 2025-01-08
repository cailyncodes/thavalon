# models/person.py

from typing import Any, Dict


class Person:
    """
    Represents a person in the game.
    """

    def __init__(self, name: str):
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the person to a dictionary.
        """
        return {
            "name": self.name
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Person':
        """
        Deserializes a person from a dictionary.
        """
        return cls(name=data["name"])

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Person):
            return self.name == other.name
        return False
