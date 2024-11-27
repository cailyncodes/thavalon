from enum import Enum

from model.person import Person

class ProposalVote(Enum):
    """
    Enum-like class for proposal votes
    """
    OPTION_1 = "Option 1"
    OPTION_2 = "Option 2"
    YES = "Yes"
    NO = "No"

    @classmethod
    def from_string(cls, string):
      """
      Converts a string to a ProposalVote
      """
      return {
        "Option 1": cls.OPTION_1,
        "Option 2": cls.OPTION_2,
        "Yes": cls.YES,
        "No": cls.NO
      }[string]

class Proposal:
    """
    Class representing a single proposal
    """

    def __init__(self, round_number: int, proposal_number: int, proposer: "Person", team=None, votes: dict[Person, ProposalVote] | None=None, passed=None):
        self.round_number = round_number
        self.proposal_number = proposal_number
        self.proposer = proposer
        self.team = team or []
        self.votes = votes or {}
        self.passed = passed

    def cast_vote(self, voter: "Person", option: ProposalVote):
        """
        Casts a vote for the proposal.
        """
        self.votes[voter] = option

    def finalize(self):
        """
        Finalizes the proposal, determining the winning option.
        """
        if self.passed is not None:
            return self

        vote_counts: dict[ProposalVote, int] = {}
        for vote in self.votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        # Handle tie logic
        if self.round_number == 1:
            # In round 1, ties default to Option 2
            if len(vote_counts) == 1 or vote_counts.get(ProposalVote.OPTION_1, 0) == vote_counts.get(ProposalVote.OPTION_2, 0):
                self.passed = self.proposal_number == 2
            else:
                self.passed = max(vote_counts, key=vote_counts.get) == (ProposalVote.OPTION_1 if self.proposal_number == 1 else ProposalVote.OPTION_2)
        else:
            # In other rounds, ties do not pass
            counts = list(vote_counts.keys())
            if len(counts) > 1 and vote_counts[counts[0]] == vote_counts[counts[1]]:
                self.passed = False
            else:
                self.passed = max(vote_counts, key=vote_counts.get) == ProposalVote.YES

        return self.passed

    def to_dict(self):
        return {
            "round_number": self.round_number,
            "proposal_number": self.proposal_number,
            "proposer": self.proposer.to_dict() if self.proposer else None,
            "team": [person.to_dict() for person in self.team],
            "votes": {person.name: vote.value for person, vote in self.votes.items()},
            "passed": self.passed,
        }
    
    @classmethod
    def from_json(cls, data):
        round_number = data["round_number"] if "round_number" in data else 1
        proposal_number = data["proposal_number"] if "proposal_number" in data else 1
        proposer = Person.from_json(data["proposer"]) if "proposer" in data else None
        team = [Person.from_json(person) for person in data["team"]] if "team" in data else []
        votes = {Person.from_json({"name": person}): ProposalVote(vote) for person, vote in data["votes"].items()} if "votes" in data else {}
        passed = data["passed"] if "passed" in data else None
        return cls(round_number, proposal_number, proposer, team, votes, passed)
