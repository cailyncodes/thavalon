"""
DAL for game
"""

import json
import os

from model.game import Game

# check if running in docker
if os.path.exists("/.dockerenv"):
    DIRECTORY = "/etc/thavalon"
else:
    DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "volume", "thavalon")


class GameDAL:
    """
    Data access layer for game
    """

    def __init__(self):
        self._directory = DIRECTORY

    def create_game(self, game: Game):
        """
        Creates a new game
        """
        # make file if it doesn't exist
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

        with open(
            f"{self._directory}/game_{game.id}.json", "x", encoding="utf-8"
        ) as file:
            print(game.to_dict())
            file.write(json.dumps(game.to_dict(), indent=2))

    def get_game(self, game_id):
        """
        Gets a game by id
        """
        with open(
            f"{self._directory}/game_{game_id}.json", "r", encoding="utf-8"
        ) as file:
            data = json.loads(file.read())
            print(data)
            return Game.from_json(data)
