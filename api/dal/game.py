# dal/game_dal.py

import json
import os
from filelock import FileLock, Timeout
from model.game import Game
from model.person import Person
from model.proposal import Proposal, ProposalVote
from model.mission import Mission, MissionVote
from model.event import Event


DIRECTORY = "/path/to/game_logs"  # Update as per your environment


class GameDAL:
    """
    Data access layer for game using Event Sourcing with file-based logs.
    """

    def __init__(self, lock_timeout=10):
        self._directory = DIRECTORY
        self._lock_timeout = lock_timeout
        if not os.path.exists(self._directory):
            os.makedirs(self._directory)

    def _get_log_file_path(self, game_id):
        return os.path.join(self._directory, f"game_{game_id}.log")

    def _get_lock_path(self, game_id):
        return self._get_log_file_path(game_id) + ".lock"

    def create_game(self, game: Game):
        """
        Initializes a new game by creating its event log.
        """
        log_file = self._get_log_file_path(game.id)
        lock_file = self._get_lock_path(game.id)
        lock = FileLock(lock_file, timeout=self._lock_timeout)

        if os.path.exists(log_file):
            raise FileExistsError(f"Game with ID {game.id} already exists.")

        event = Event(
            event_type="GameCreated",
            payload=game.to_dict()
        )

        try:
            with lock:
                with open(log_file, "a", encoding="utf-8") as file:
                    file.write(json.dumps(event.to_dict()) + "\n")
        except Timeout:
            raise TimeoutError(f"Could not acquire lock for creating game {game.id}.")

    def _replay_events(self, game_id) -> Game:
        """
        Reconstructs the game state by replaying all events.
        """
        log_file = self._get_log_file_path(game_id)
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"Game with ID {game_id} does not exist.")

        lock_file = self._get_lock_path(game_id)
        lock = FileLock(lock_file, timeout=self._lock_timeout)

        game = None

        try:
            with lock:
                with open(log_file, "r", encoding="utf-8") as file:
                    for line in file:
                        event_data = json.loads(line)
                        event = Event.from_dict(event_data)
                        if event.event_type == "GameCreated":
                            game = Game.from_json(event.payload)
                        else:
                            game.apply_event(event)
        except Timeout:
            raise TimeoutError(f"Could not acquire lock for reading game {game_id}.")

        return game

    def get_game(self, game_id):
        return self._replay_events(game_id)

    def append_event(self, game_id: str, event: Event):
        log_file = self._get_log_file_path(game_id)
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"Game with ID {game_id} does not exist.")

        lock_file = self._get_lock_path(game_id)
        lock = FileLock(lock_file, timeout=self._lock_timeout)

        try:
            with lock:
                with open(log_file, "a", encoding="utf-8") as file:
                    file.write(json.dumps(event.to_dict()) + "\n")
        except Timeout:
            raise TimeoutError(f"Could not acquire lock for updating game {game_id}.")

    # Updated methods to handle simplified voting
    def add_proposal(self, game_id: str, proposer: Person, team: list[Person]):
        game = self.get_game(game_id)
        proposal = game.create_proposal(proposer, team)
        event = Event(
            event_type="ProposalAdded",
            payload={
                "round_number": proposal.round_number,
                "proposal_number": proposal.proposal_number,
                "proposer": proposer.to_dict(),
                "team": [person.to_dict() for person in team]
            }
        )
        self.append_event(game_id, event)
        return game

    def add_proposal_vote(self, game_id: str, voter: Person, option: ProposalVote):
        game = self.get_game(game_id)
        game.add_proposal_vote(voter, option)
        event = Event(
            event_type="ProposalVoteAdded",
            payload={
                "voter": voter.to_dict(),
                "option": option.value  # "Yes" or "No"
            }
        )
        self.append_event(game_id, event)
        return game

    def add_mission_vote(self, game_id: str, voter: Person, vote: MissionVote):
        game = self.get_game(game_id)
        game.add_mission_vote(voter, vote)
        event = Event(
            event_type="MissionVoteAdded",
            payload={
                "voter": voter.to_dict(),
                "vote": vote.value
            }
        )
        self.append_event(game_id, event)
        return game

    # Implement other methods similarly
