"""
Manager class for the game.
"""

import random
from copy import deepcopy

from dal.game import GameDAL
from model.game import Game
from model.player import Player
from model.role import ALL_ROLES


class GameManager:
    """
    Manager class for the game.

    Maintains a list of all active games in a dictionary by game id.
    """

    def __init__(self, game_dal: GameDAL):
        self._game_dal = game_dal

    def create_game(self, persons):
        """
        Creates a new game with the given players and persons.
        """
        players = self._assign_roles(persons)
        game = Game(players, persons)
        self._game_dal.create_game(game)
        return game

    def get_game(self, game_id):
        """
        Gets a game by game id.
        """
        return self._game_dal.get_game(game_id)

    def _assign_roles(self, all_persons):
        """
        Assigns roles to the players in the game.
        """
        num_players = len(all_persons)
        players = list()

        while len(players) < num_players:
            # duplicate initialization b/c we can't do a do/while loop in python
            players = list()

            roles = deepcopy(ALL_ROLES)
            random.shuffle(roles)
            persons = deepcopy(all_persons)
            random.shuffle(persons)

            while len(roles) > 0:
                next_role = roles.pop()()
                current_roles = [player.role for player in players]
                (can_use, necessary_additions) = next_role.ensure_constraints(
                    current_roles, num_players
                )
                if not can_use:
                    continue

                for role in [next_role] + [role() for role in necessary_additions]:
                    person = persons.pop()
                    player = Player(person, role)
                    players.append(player)

                if len(players) == num_players:
                    break

        print(players)
        return players
