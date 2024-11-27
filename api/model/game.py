"""
Class representing a game
"""

from base64 import b64decode, b64encode
from copy import deepcopy
from datetime import datetime
from random import randint, shuffle

from model.mission import Mission, MissionVote
from model.person import Person
from model.player import Player
from model.proposal import Proposal, ProposalVote

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
  Class representing a game

  Attributes:
    id (int): The id of the game
    name (str): The name of the game
    starting_person (Person): The starting person
    persons (List[Person]): The persons in the game
    players (List[Player]): The players in the game
    status (str): The status of the game
    variant (str): The variant of the game
    proposal_round (int): The current proposal round
    mission_number (int): The current mission number
    proposals (List[Proposal]): The proposals in the game
    missions (List[Mission]): The missions in the game
  """

  def __init__(
      self,
      name: str,
      persons: list["Person"],
      players: list["Player"],
      proposals: list["Proposal"] = None,
      missions: list["Mission"] = None,
      status="open",
      variant="thavalon"
    ):
    # ignore linter warning, random key is used to ensure that the game id is unique
    # pylint: disable=unused-private-member
    self.__random_key = datetime.now().timestamp() + abs(hash(name)) + randint(0, 10000)
    self.name = name
    self.persons = persons
    self.players = players
    self.status = status
    self.variant = variant

    self.num_players = len(players)
    self.max_proposals = HAMMER_COUNTS[self.num_players] if self.num_players in HAMMER_COUNTS else None
    self.mission_sizes = MISSION_COUNTS[self.num_players] if self.num_players in MISSION_COUNTS else None
    self.proposal_round = 1
    self.mission_number = 1
    self.proposals: list["Proposal"] = proposals or []
    self.missions = missions or ([Mission(round_number=i + 1, required_team_size=size) for i, size in enumerate(self.mission_sizes)] if self.status == "in-progress" else [])
        
    self.__id = None
    self.__starting_person = None

  def __str__(self):
    return str(self.to_dict())

  def __repr__(self):
    return f"Game<{self.id}>: {self.name} ({self.status})"
  
  def __hash__(self):
    return hash(self.__random_key)

  def to_dict(self):
    """
    Returns a dictionary representation of the game
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
  def from_json(cls, data):
    """
    Updates the game from a dictionary representation
    """
    name = data["name"]
    persons = [Person.from_json(person) for person in data["persons"]]
    players = [Player.from_json(player) for player in data["players"]]
    proposals = [Proposal.from_json(proposal) for proposal in data.get("proposals", [])]
    missions = [Mission.from_json(mission) for mission in data["missions"]] if "missions" in data else []
    status = data["status"] if "status" in data else "open"
    variant = data["variant"] if "variant" in data else "thavalon"
    
    game = cls(name, persons, players, proposals, missions, status, variant)

    id = data.get("id", None)
    starting_person = Person.from_json(data["starting_person"]) if "starting_person" in data else None
    proposal_round = data.get("proposal_round", 1)
    mission_number = data.get("mission_number", 1)
    
    game.__id = int(b64decode(id).decode("utf-8"), base=16) if id else None
    game.__starting_person = starting_person
    game.proposal_round = proposal_round
    game.mission_number = mission_number
    return game

  @property
  def id(self):
    """
    Returns the id of the game
    """
    if self.__id is not None:
      return self.__id

    self.__id = hash(self)
    return self.__id

  @property
  def starting_person(self):
    """
    Returns the starting player
    """
    if self.__starting_person is None and len(self.players) > 0:
      players = deepcopy(self.players)
      shuffle(players)
      self.__starting_person = players[0].person

    return self.__starting_person
  
  def get_roles(self):
    """
    Returns the roles of the players in the game
    """
    return [player.role for player in self.players]
  
  def create_proposal(self, proposer: "Person", team: list["Person"]):
    """
    Creates a new proposal for the current round.
    """
    if self.proposal_round > self.max_proposals:
        raise ValueError("Maximum number of proposals reached.")
    
    if (self.mission_number == 1 and self.proposal_round == 1 and len(self.proposals) == 1):
      self.proposal_round += 1

    proposal = Proposal(round_number=self.mission_number, proposal_number=self.proposal_round, proposer=proposer, team=team)
    self.proposals.append(proposal)
    return proposal

  def add_proposal_vote(self, voter: "Person", option: "ProposalVote"):
    """
    Adds a vote to the current proposal.
    """
    if not self.proposals:
      raise ValueError("No active proposal.")

    if self.mission_number == 1:
      option_1_proposal = self.proposals[0]
      option_2_proposal = self.proposals[-1]
      option_1_proposal.cast_vote(voter, option)
      option_2_proposal.cast_vote(voter, option)
    else:
      current_proposal = self.proposals[-1]
      current_proposal.cast_vote(voter, option)

  def add_mission_vote(self, voter: "Person", vote: "MissionVote"):
    """
    Adds a vote to the specified mission.
    """
    mission_number = self.mission_number
    if mission_number < 1 or mission_number > len(self.missions):
      raise ValueError("Invalid mission number.")

    mission = self.missions[mission_number - 1]
    mission.cast_vote(voter, vote)

    if len(mission.votes.items()) == len(self.players):
      mission.finalize()
      self.mission_number += 1
