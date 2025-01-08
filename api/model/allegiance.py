# models/allegiance.py

from enum import Enum


class Allegiance(Enum):
    """
    Enum representing player allegiances.
    """
    GOOD = "Good"
    BAD = "Bad"
