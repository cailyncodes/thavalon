# models/mission_vote.py

from enum import Enum


class MissionVote(Enum):
    """
    Enum representing possible mission votes.
    """
    SUCCESS = "Success"
    FAIL = "Fail"
    REVERSE = "Reverse"
    CANCEL = "Cancel"

    @classmethod
    def from_string(cls, string: str) -> 'MissionVote':
        """
        Converts a string to a MissionVote enum.
        """
        return {
            "Success": cls.SUCCESS,
            "Fail": cls.FAIL,
            "Reverse": cls.REVERSE,
            "Cancel": cls.CANCEL
        }[string]
