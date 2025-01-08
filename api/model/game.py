# models/game.py

from base64 import b64decode, b64encode
from copy import deepcopy
from datetime import datetime
from random import randint, shuffle
from typing import Any, List, Optional, Dict

from model.event import Event
from model.mission import Mission
from model.mission_vote import MissionVote
from model.person import Person
from model.player import Player
from model.proposal import Proposal, ProposalVote
from model.role import Role
from model.role_name import RoleName


HAMMER_COUNTS = {
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 4,
    10: 5
}

MISSION_COUNTS = {
    5: [2, 3, 2, 3, 3],
    6: [2, 3, 4, 3, 4],
    7: [2, 3, 3, 4, 4],
    8: [3, 4, 4, 5, 5],
    9: [3, 4, 4, 5, 5],
    10: [3, 4, 4, 5, 5],
}


class Game:
    """
    Represents a game.
    """

    def __init__(
        self,
        name: str,
        persons: List[Person],
        players: List[Player],
        proposals: Optional[List[Proposal]] = None,
        missions: Optional[List[Mission]] = None,
        status: str = "open",
        variant: str = "thavalon"
    ):
        self.__random_key = datetime.now().timestamp() + abs(hash(name)) + randint(0, 10000)
        self.name = name
        self.persons = persons
        self.players = players
        self.status = status
        self.variant = variant

        self.num_players = len(players)
        self.max_proposals = HAMMER_COUNTS.get(self.num_players)
        self.mission_sizes = MISSION_COUNTS.get(self.num_players)
        self.proposal_round = 1
        self.mission_number = 1
        self.proposals: List[Proposal] = proposals or []
        self.missions = missions or (
            [Mission(round_number=i + 1, required_team_size=size) for i, size in enumerate(self.mission_sizes)]
            if self.status == "in-progress"
            else []
        )

        self.__id: Optional[int] = None
        self.__starting_person: Optional[Person] = None

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return f"Game<{self.id}>: {self.name} ({self.status})"

    def __hash__(self):
        return hash(self.__random_key)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the game to a dictionary.
        """
        return {
            "id": b64encode(hex(self.id).encode("utf-8")).decode("utf-8"),
            "name": self.name,
            "starting_person": self.starting_person.to_dict() if self.starting_person else None,
            "persons": [person.to_dict() for person in self.persons],
            "players": [player.to_dict(self) for player in self.players],
            "status": self.status,
            "variant": self.variant,
            "proposal_round": self.proposal_round,
            "mission_number": self.mission_number,
            "proposals": [proposal.to_dict() for proposal in self.proposals],
            "missions": [mission.to_dict() for mission in self.missions],
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Game':
        """
        Deserializes a game from a dictionary.
        """
        name = data["name"]
        persons = [Person.from_json(person) for person in data["persons"]]
        players = [Player.from_json(player) for player in data["players"]]
        proposals = [Proposal.from_json(proposal) for proposal in data.get("proposals", [])]
        missions = [Mission.from_json(mission) for mission in data.get("missions", [])]
        status = data.get("status", "open")
        variant = data.get("variant", "thavalon")

        game = cls(name, persons, players, proposals, missions, status, variant)

        id_encoded = data.get("id")
        game.__id = int(b64decode(id_encoded).decode("utf-8"), 16) if id_encoded else None
        starting_person_data = data.get("starting_person")
        game.__starting_person = Person.from_json(starting_person_data) if starting_person_data else None
        game.proposal_round = data.get("proposal_round", 1)
        game.mission_number = data.get("mission_number", 1)

        return game

    def apply_event(self, event: 'Event'):
        """
        Applies an event to mutate the game state.
        """
        if event.event_type == "GameCreated":
            # Initialization is already handled via from_json
            pass
        elif event.event_type == "ProposalAdded":
            proposal = Proposal.from_json(event.payload)
            self.proposals.append(proposal)
        elif event.event_type == "ProposalVoteAdded":
            voter = Person.from_json(event.payload["voter"])
            option = ProposalVote.from_string(event.payload["option"])
            self.add_proposal_vote(voter, option)
        elif event.event_type == "MissionVoteAdded":
            voter = Person.from_json(event.payload["voter"])
            vote = MissionVote.from_string(event.payload["vote"])
            self.add_mission_vote(voter, vote)
        # Add more event types as needed

    @classmethod
    def from_event_log(cls, events: List['Event']) -> 'Game':
        """
        Reconstructs the game state by applying a list of events.
        """
        game = None
        for event in events:
            if event.event_type == "GameCreated":
                game = cls.from_json(event.payload)
            else:
                game.apply_event(event)
        return game

    @property
    def id(self) -> Optional[int]:
        """
        Returns the ID of the game.
        """
        if self.__id is not None:
            return self.__id

        self.__id = hash(self)
        return self.__id

    @property
    def starting_person(self) -> Optional[Person]:
        """
        Returns the starting player.
        """
        if self.__starting_person is None and len(self.players) > 0:
            players = deepcopy(self.players)
            shuffle(players)
            self.__starting_person = players[0].person

        return self.__starting_person

    def get_roles(self) -> List[RoleName]:
        """
        Returns the roles of the players in the game.
        """
        return [player.role.name for player in self.players if player.role]

    def create_proposal(self, proposer: Person, team: List[Person]) -> Proposal:
        """
        Creates a new proposal for the current round.
        """
        if self.proposal_round > self.max_proposals:
            raise ValueError("Maximum number of proposals reached.")

        proposal = Proposal(
            round_number=self.mission_number,
            proposal_number=self.proposal_round,
            proposer=proposer,
            team=team
        )
        self.proposals.append(proposal)
        return proposal

    def add_proposal_vote(self, voter: Person, option: ProposalVote):
        """
        Adds a vote to the current proposal.
        """
        if not self.proposals:
            raise ValueError("No active proposal.")

        current_proposal = self.proposals[-1]
        current_proposal.cast_vote(voter, option)

        # Optionally finalize the proposal if all players have voted
        if len(current_proposal.votes) == len(self.players):
            current_proposal.finalize()
            if current_proposal.passed:
                # Assign the proposed team to the mission
                mission = self.missions[self.mission_number - 1]
                mission.assign_team(current_proposal.team)
                # Proceed to the mission phase
                self.proposal_round = 1
                # Update mission number if necessary
                self.mission_number += 1
            else:
                # Increment the proposal round or handle proposal failure
                self.proposal_round += 1
                if self.proposal_round > self.max_proposals:
                    # Handle hammer failed scenario
                    # For example, assign empty team, mark mission as failed, etc.
                    mission = self.missions[self.mission_number - 1]
                    mission.assign_team([])
                    mission.result = False
                    self.mission_number += 1

    def add_mission_vote(self, voter: Person, vote: MissionVote):
        """
        Adds a vote to the specified mission.
        """
        mission_number = self.mission_number
        if mission_number < 1 or mission_number > len(self.missions):
            raise ValueError("Invalid mission number.")

        mission = self.missions[mission_number - 1]
        mission.cast_vote(voter, vote)

        if len(mission.votes) == len(self.players):
            mission.finalize()
            self.mission_number += 1

            # Check if the game has been won by either side
            successful_missions = [mission for mission in self.missions if mission.result]
            if len(successful_missions) >= 3 or len(self.missions) - len(successful_missions) >= 3:
                self.status = "closed"
