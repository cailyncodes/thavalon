"""
Manager class for the game.
"""

import random
from copy import deepcopy

from dal.game import GameDAL
from model.game import Game
from model.mission import MissionVote
from model.person import Person
from model.player import Player
from model.proposal import ProposalVote
from model.role import ALL_ROLES
from util.word import get_random_english_word


class GameManager:
  """
  Manager class for the game.

  Maintains a list of all active games in a dictionary by game id.
  """

  def __init__(self, game_dal: GameDAL):
    self._game_dal = game_dal

  def get_game(self, game_id):
    """
    Gets a game by game id.
    """
    return self._game_dal.get_game(game_id)
  
  def list_games_by_status(self):
    """
    Lists all games by status.
    """
    return self._game_dal.list_games_by_status()

  def create_game(self, persons):
    """
    Creates a new game with the given players and persons.
    """
    name = get_random_english_word()
    persons = [Person.from_json(person) for person in persons if person]
    players: list[Player] = []
    game = Game(name, persons, players, status="open")
    self._game_dal.create_game(game)
    return game
  
  def join_game(self, game_id, person):
    """
    Adds a player to an existing game.
    """
    game = self.get_game(game_id)
    if game.status != "open":
      raise Exception("Cannot join a game that is not open.")
    
    new_person = Person.from_json(person)
    game.persons.append(new_person)
    self._game_dal.update_game(game)
    return game

  def assign_roles_and_start_game(self, game_id, variant):
    """
    Assigns roles and starts a game by game id.
    """
    game = self.get_game(game_id)
    players = self._assign_roles(game.persons, variant)
    self._game_dal.update_game(game, players=players, status="in-progress")

  def add_proposal(self, game_id: str, proposer: Person, team: list[Person]):
    """
    Adds a proposal to a game by game id.
    """
    return self._game_dal.add_proposal(game_id, proposer, team)
  
  def add_proposal_vote(self, game_id: str, voter: Person, option: ProposalVote):
    """
    Adds a proposal vote to a game by game id.
    """
    return self._game_dal.add_proposal_vote(game_id, voter, option)
  
  def add_mission_vote(self, game_id: str, voter: Person, vote: MissionVote):
    """
    Adds a mission vote to a game by game id.
    """
    return self._game_dal.add_mission_vote(game_id, voter, vote)

  def close_game(self, game_id):
    """
    Closes a game by game id.
    """
    game = self.get_game(game_id)
    self._game_dal.update_game(game, status="closed")

  def _assign_roles(self, all_persons, variant="thavalon"):
    """
    Assigns roles to the players in the game.
    """
    num_players = len(all_persons)
    filtered_roles = [role for role in ALL_ROLES if role.can_use_for_variant(variant)]

    while True:
      persons = deepcopy(all_persons)
      random.shuffle(persons)
      
      players: list['Player'] = []
      
      roles = sorted(filtered_roles, key=lambda role: role.priority(num_players), reverse=False)

      while roles and len(players) < num_players:
          next_role = roles.pop()
          current_roles = [player.role for player in players]
          can_use, necessary_additions = next_role.ensure_constraints(
            current_roles, num_players
          )
          if not can_use:
            continue

          # Assign next_role and necessary_additions
          roles_to_assign = [next_role] + necessary_additions
          # Check if there are enough persons
          if len(persons) < len(roles_to_assign):
            break  # Not enough persons, retry

          for role in roles_to_assign:
            person = persons.pop()
            player = Player(person, role)
            players.append(player)

            # # Remove the role from the roles list to prevent duplicate assignments
            # if role in roles:
            #   roles.remove(role)

          if len(players) == num_players:
            break

      if len(players) == num_players:
        return players
