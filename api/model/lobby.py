"""
Class representing a lobby
"""

from base64 import b64encode
from .person import Person


class Lobby:
    """
    Class representing a lobby

    Attributes:
      lobby_id (int): The
      name (str): The name of the lobby
      persons (List[Person]): The persons in the lobby
      game_id (str)
      status (str)
    """

    def __init__(self, lobby_id, name, persons):
        self.lobby_id = lobby_id
        self.name = name
        self.persons = persons
        self.game_id = None
        self.status = "open"

    def __str__(self):
        return f"Lobby {self.name} ({self.lobby_id}) with {len(self.persons)} persons"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Returns a dictionary representation of the lobby
        """
        return {
            "lobby_id": self.lobby_id,
            "name": self.name,
            "persons": [person.to_dict() for person in self.persons],
            "game_id": (
                b64encode(hex(self.game_id).encode("utf-8")).decode("utf-8")
                if self.game_id
                else None
            ),
            "status": self.status,
        }

    @classmethod
    def from_json(cls, data):
        """
        Updates the lobby from a dictionary representation
        """
        lobby_id = data["lobby_id"]
        name = data["name"]
        persons = [Person.from_json(person) for person in data["persons"]]
        return cls(lobby_id, name, persons)
