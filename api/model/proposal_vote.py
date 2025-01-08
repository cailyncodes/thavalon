# models/proposal_vote.py

from enum import Enum


class ProposalVote(Enum):
    """
    Enum representing possible proposal votes.
    """
    YES = "Yes"
    NO = "No"

    @classmethod
    def from_string(cls, string: str) -> 'ProposalVote':
        """
        Converts a string to a ProposalVote enum.
        """
        try:
            return cls[string.upper()]
        except KeyError:
            raise ValueError(f"Invalid ProposalVote: {string}")
