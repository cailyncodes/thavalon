from enum import Enum

from model.person import Person

class MissionVote(Enum):
    """
    Enum-like class for mission votes
    """
    SUCCESS = "Success"
    FAIL = "Fail"
    REVERSE = "Reverse"
    CANCEL = "Cancel"

    @classmethod
    def from_string(cls, string):
      """
      Converts a string to a ProposalVote
      """
      return {
        "Success": cls.SUCCESS,
        "Fail": cls.FAIL,
        "Reverse": cls.REVERSE,
        "Cancel": cls.CANCEL
      }[string]

class Mission:
    """
    Class representing a single mission
    """

    def __init__(self, round_number: int, required_team_size: int, team: list[Person] | None=None, votes: dict[Person, MissionVote] | None=None, result: bool | None=None):
        self.round_number = round_number
        self.required_team_size = required_team_size
        self.team = team or []
        self.votes = votes or {}
        self.result = result

    def assign_team(self, team: list["Person"]):
        """
        Assigns a team to the mission.
        """
        if len(team) != self.required_team_size:
            raise ValueError(f"Team size must be {self.required_team_size}, got {len(team)}.")
        self.team = team

    def cast_vote(self, voter: "Person", vote: MissionVote):
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

    def to_dict(self):
        """
        Returns a dictionary representation of the mission
        """
        return {
            "round_number": self.round_number,
            "required_team_size": self.required_team_size,
            "team": [person.to_dict() for person in self.team],
            "votes": {person.name: vote.value for person, vote in self.votes.items()},
            "result": self.result
        }
    
    @classmethod
    def from_json(cls, data):
        """
        Updates the mission from a dictionary representation
        """
        round_number = data["round_number"] if "round_number" in data else 1
        required_team_size = data["required_team_size"] if "required_team_size" in data else 1
        team = [Person.from_json(player) for player in data["team"]] if "team" in data else []
        votes = {Person.from_json({"name": person}): MissionVote(vote) for person, vote in data["votes"].items()} if "votes" in data else {}
        result = data["result"] if data["result"] is not None else None if "result" in data else None
        mission = cls(round_number, required_team_size, team, votes, result)
        return mission
