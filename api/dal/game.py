"""
DAL for game with file locking
"""

import json
import os

from filelock import FileLock, Timeout

from model.game import Game
from model.mission import MissionVote
from model.person import Person
from model.proposal import Proposal, ProposalVote

# Check if running in Docker
if os.path.exists("/.dockerenv"):
  DIRECTORY = "/etc/thavalon"
else:
  DIRECTORY = os.path.join(os.path.dirname(__file__), "..", "volume")


class GameDAL:
  """
  Data access layer for game with file locking
  """

  def __init__(self, lock_timeout=10):
    """
    Initializes the GameDAL.

    :param lock_timeout: Maximum time (in seconds) to wait for acquiring the lock.
    """
    self._directory = DIRECTORY
    self._lock_timeout = lock_timeout
    if not os.path.exists(self._directory):
      os.makedirs(self._directory)

  def _get_game_file_path(self, game_id):
    """
    Helper method to get the file path for a given game ID.

    :param game_id: The ID of the game.
    :return: The file path as a string.
    """
    return os.path.join(self._directory, f"game_{game_id}.json")

  def _get_lock_path(self, game_id):
    """
    Helper method to get the lock file path for a given game ID.

    :param game_id: The ID of the game.
    :return: The lock file path as a string.
    """
    return self._get_game_file_path(game_id) + ".lock"

  def create_game(self, game: Game):
    """
    Creates a new game with file locking to prevent race conditions.

    :param game: The Game object to create.
    :raises FileExistsError: If the game file already exists.
    """
    game_file = self._get_game_file_path(game.id)
    lock_file = self._get_lock_path(game.id)
    lock = FileLock(lock_file, timeout=self._lock_timeout)

    try:
      with lock:
        if os.path.exists(game_file):
          raise FileExistsError(f"Game with ID {game.id} already exists.")
        with open(game_file, "w", encoding="utf-8") as file:
          file.write(json.dumps(game.to_dict(), indent=2))
    except Timeout:
      raise TimeoutError(f"Could not acquire lock for creating game {game.id}.")

  def get_game(self, game_id):
    """
    Gets a game by ID with optional locking for safe read operations.

    :param game_id: The ID of the game to retrieve.
    :return: The Game object.
    :raises FileNotFoundError: If the game file does not exist.
    """
    game_file = self._get_game_file_path(game_id)
    if not os.path.exists(game_file):
      raise FileNotFoundError(f"Game with ID {game_id} does not exist.")

    lock_file = self._get_lock_path(game_id)
    lock = FileLock(lock_file, timeout=self._lock_timeout)

    try:
      with lock:
        with open(game_file, "r", encoding="utf-8") as file:
          data = json.load(file)
          return Game.from_json(data)
    except Timeout:
      raise TimeoutError(f"Could not acquire lock for reading game {game_id}.")

  def update_game(self, game: Game, players=None, status=None, variant=None):
    """
    Updates an existing game with file locking to ensure safe writes.

    :param game: The Game object to update.
    :param players: Optional list of players to update.
    :param status: Optional status to update.
    :raises FileNotFoundError: If the game file does not exist.
    """
    game_file = self._get_game_file_path(game.id)
    if not os.path.exists(game_file):
      raise FileNotFoundError(f"Game with ID {game.id} does not exist.")

    lock_file = self._get_lock_path(game.id)
    lock = FileLock(lock_file, timeout=self._lock_timeout)

    try:
      with lock:
        if players is not None:
          game.players = players
        if status is not None:
          game.status = status
        if variant is not None:
          game.variant = variant
        # apply all the necessary changes in here, so that we already have the file lock
        # this is a bit of a hack, but it's the easiest way to ensure that the game is in a 
        # consistent state before we write it to disk
        self.apply_proposal_votes(game)
        self.apply_mission_vote(game)

        with open(game_file, "w", encoding="utf-8") as file:
          file.write(json.dumps(game.to_dict(), indent=2))

    except Timeout:
      raise TimeoutError(f"Could not acquire lock for updating game {game.id}.")

  def list_games_by_status(self):
    """
    Lists all games by status. This method uses individual file locks for each game file.

    :return: A dictionary categorizing games by their status.
    """
    games = {}
    for filename in os.listdir(self._directory):
      if filename.startswith("game_") and filename.endswith(".json"):
        game_id = filename[len("game_") : -len(".json")]
        game_file = os.path.join(self._directory, filename)
        lock_file = game_file + ".lock"
        lock = FileLock(lock_file, timeout=self._lock_timeout)

        try:
          with lock:
            with open(game_file, "r", encoding="utf-8") as file:
              try:
                data = json.load(file)
                # Validate required fields
                if not all(
                  key in data
                  for key in ["name", "persons", "players", "status"]
                ):
                  continue
                game = Game.from_json(data)

                if games.get(game.status) is None:
                  games[game.status] = []

                if (
                  game.status == "closed"
                  and game.starting_person is None
                ):
                  continue

                games[game.status].append(game)
              except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {filename}: {e}")
                continue

        except Timeout:
          print(
            f"Could not acquire lock for listing game {game_id}. Skipping."
          )

    return games
  
  def add_proposal(self, game_id: str, proposer: Person, team: list[Person]):
    game = self.get_game(game_id)
    game.create_proposal(proposer, team)
    self.update_game(game)
    return game

  def add_proposal_vote(self, game_id: str, voter: Person, option: ProposalVote):
    game = self.get_game(game_id)
    game.add_proposal_vote(voter, option)
    self.update_game(game)
    return game

  def add_mission_vote(self, game_id, voter: str, vote: MissionVote):
    game = self.get_game(game_id)
    game.add_mission_vote(voter, vote)
    self.update_game(game)
    return game
  
  def apply_proposal_votes(self, game: Game):
    """
    Applies the votes for the current proposal.
    """
    if not game.proposals:
      return
    
    if game.mission_number > 5 or game.status == "closed":
      return
    
    current_mission = game.missions[game.mission_number - 1]
    if current_mission.result is None and len(current_mission.team) == current_mission.required_team_size and len(current_mission.votes.items()) <= current_mission.required_team_size:
      return

    proposals_to_finalize: list[Proposal] = []

    if game.mission_number == 1:
      proposals_to_finalize.append(game.proposals[0])
      
    proposals_to_finalize.append(game.proposals[-1])

    successful_proposal = None
    for proposal in proposals_to_finalize:
      if len(proposal.votes.items()) != len(game.players):
        return
      if proposal.finalize():
        successful_proposal = proposal

    if successful_proposal is not None:
      game.proposal_round = 1
      mission = game.missions[game.mission_number - 1]
      mission.assign_team(successful_proposal.team)
    # hammer failed
    if successful_proposal is None and game.proposal_round == game.max_proposals:
      game.proposal_round = 1
      mission = game.missions[game.mission_number - 1]
      mission.assign_team([])
      mission.result = "Fail"
      game.mission_number += 1
  
    if successful_proposal is None:
      game.proposal_round += 1

  def apply_mission_vote(self, game: Game):
    if not game.missions:
      return

    if game.starting_person is None or game.mission_number > 5 or game.status == "closed":
      return

    current_mission = game.missions[game.mission_number - 1]
    if current_mission.result is None and current_mission.required_team_size == len(current_mission.votes.items()):
      current_mission.finalize()
      game.mission_number += 1

    successful_missions = [mission for mission in game.missions if mission.result]
    if len(successful_missions) >= 3:
      game.status = "closed"
