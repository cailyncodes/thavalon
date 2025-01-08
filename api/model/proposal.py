# models/proposal.py

from typing import Any, Dict, List, Optional
from model.person import Person
from model.proposal_vote import ProposalVote


class Proposal:
    """
    Represents a single proposal in the game.
    """

    def __init__(
        self,
        round_number: int,
        proposal_number: int,
        proposer: Person,
        team: Optional[List[Person]] = None,
        votes: Optional[Dict[Person, ProposalVote]] = None,
        passed: Optional[bool] = None
    ):
        self.round_number = round_number
        self.proposal_number = proposal_number
        self.proposer = proposer
        self.team = team or []
        self.votes = votes or {}
        self.passed = passed

    def cast_vote(self, voter: Person, option: ProposalVote):
        """
        Casts a vote for the proposal.
        """
        if option not in ProposalVote:
            raise ValueError(f"Invalid vote option: {option}")
        self.votes[voter] = option

    def finalize(self):
        """
        Finalizes the proposal, determining if it passed based on majority 'Yes' votes.
        """
        if self.passed is not None:
            return self.passed

        vote_counts: Dict[ProposalVote, int] = {}
        for vote in self.votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        yes_votes = vote_counts.get(ProposalVote.YES, 0)
        no_votes = vote_counts.get(ProposalVote.NO, 0)

        # Determine if the proposal passes by majority 'Yes' votes
        self.passed = yes_votes > no_votes

        return self.passed

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the proposal to a dictionary.
        """
        return {
            "round_number": self.round_number,
            "proposal_number": self.proposal_number,
            "proposer": self.proposer.to_dict() if self.proposer else None,
            "team": [person.to_dict() for person in self.team],
            "votes": {person.name: vote.value for person, vote in self.votes.items()},
            "passed": self.passed,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Proposal':
        """
        Deserializes a proposal from a dictionary.
        """
        round_number = data.get("round_number", 1)
        proposal_number = data.get("proposal_number", 1)
        proposer = Person.from_json(data["proposer"]) if "proposer" in data else None
        team = [Person.from_json(person) for person in data.get("team", [])]
        votes = {
            Person.from_json({"name": person}): ProposalVote.from_string(vote)
            for person, vote in data.get("votes", {}).items()
        }
        passed = data.get("passed")
        return cls(round_number, proposal_number, proposer, team, votes, passed)
