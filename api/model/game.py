"""
Class representing a game
"""

from base64 import b64encode
from copy import deepcopy
from datetime import datetime
from random import shuffle

from .person import Person
from .player import Player


class Game:
    """
    Class representing a game

    Attributes:
      players (List[Player]): The players in the game
    """

    def __init__(self, players, persons):
        # ignore linter warning, random key is used to ensure that the game id is unique
        # pylint: disable=unused-private-member
        self.__random_key = datetime.now().timestamp()
        self.__starting_person = None
        self.players = players
        self.persons = persons

    def __str__(self):
        return f"Game with {len(self.players)} players"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Returns a dictionary representation of the game
        """
        return {
            "id": b64encode(hex(self.id).encode("utf-8")).decode("utf-8"),
            "players": [player.to_dict(self) for player in self.players],
            "persons": [person.to_dict() for person in self.persons],
            "starting_person": self.starting_person.to_dict(),
        }

    @classmethod
    def from_json(cls, data):
        """
        Updates the game from a dictionary representation
        """
        players = [Player.from_json(player) for player in data["players"]]
        persons = [Person.from_json(person) for person in data["persons"]]
        starting_person = Person.from_json(data["starting_person"])
        game = cls(players, persons)
        game.__starting_person = starting_person
        return game

    @property
    def id(self):
        """
        Returns the id of the game
        """
        return id(self)

    @property
    def starting_person(self):
        """
        Returns the starting player
        """
        if self.__starting_person is None:
            players = deepcopy(self.players)
            shuffle(players)
            self.__starting_person = players[0].person

        return self.__starting_person
