# models/mission.py

from typing import Any, Dict, List, Optional
from model.person import Person
from model.mission_vote import MissionVote


class Mission:
    """
    Represents a single mission in the game.
    """

    def __init__(
        self,
        round_number: int,
        required_team_size: int,
        team: Optional[List[Person]] = None,
        votes: Optional[Dict[Person, MissionVote]] = None,
        result: Optional[bool] = None
    ):
        self.round_number = round_number
        self.required_team_size = required_team_size
        self.team = team or []
        self.votes = votes or {}
        self.result = result

    def assign_team(self, team: List[Person]):
        """
        Assigns a team to the mission.
        """
        if len(team) != self.required_team_size:
            raise ValueError(f"Team size must be {self.required_team_size}, got {len(team)}.")
        self.team = team

    def cast_vote(self, voter: Person, vote: MissionVote):
        """
        Casts a vote for the mission.
        """
        self.votes[voter] = vote

    def finalize(self):
        """
        Finalizes the mission, determining the result.
        """
        votes = self.votes.values()
        success_count = list(votes).count(MissionVote.SUCCESS)
        fail_count = list(votes).count(MissionVote.FAIL)
        reverse_count = list(votes).count(MissionVote.REVERSE)
        cancel_count = list(votes).count(MissionVote.CANCEL)

        if cancel_count > 0:
            self.result = False
        elif success_count == len(votes):
            self.result = True
        elif reverse_count % 2 == 1 and fail_count > 0:
            self.result = True
        else:
            self.result = False
        return self.result

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the mission to a dictionary.
        """
        return {
            "round_number": self.round_number,
            "required_team_size": self.required_team_size,
            "team": [person.to_dict() for person in self.team],
            "votes": {person.name: vote.value for person, vote in self.votes.items()},
            "result": self.result
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Mission':
        """
        Deserializes a mission from a dictionary.
        """
        round_number = data.get("round_number", 1)
        required_team_size = data.get("required_team_size", 1)
        team = [Person.from_json(player) for player in data.get("team", [])]
        votes = {
            Person.from_json({"name": person}): MissionVote.from_string(vote)
            for person, vote in data.get("votes", {}).items()
        }
        result = data.get("result")
        return cls(round_number, required_team_size, team, votes, result)
