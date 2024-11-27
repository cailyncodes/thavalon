"""
Class representing a person
"""


class Person:
  """
  Class representing a person
  """

  def __init__(self, name: str):
    self.name = name

  def __str__(self):
    return f"{self.name}"

  def __repr__(self):
    return self.__str__()

  def to_dict(self):
    """
    Returns a dictionary representation of the person
    """
    return {
      "name": self.name
    }

  @classmethod
  def from_json(cls, data):
    """
    Updates the person from a dictionary representation
    """
    if not data:
      return None
    name = data["name"]
    return cls(name)
