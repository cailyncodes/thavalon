"""
Class representing a person
"""


class Person:
    """
    Class representing a person
    """

    def __init__(self, name, login, password):
        self.name = name
        self.login = login
        self.password = password

    def __str__(self):
        return f"{self.name} ({self.login})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        """
        Returns a dictionary representation of the person
        """
        return {
            "name": self.name,
            "login": self.login,
        }

    @classmethod
    def from_json(cls, data):
        """
        Updates the person from a dictionary representation
        """
        name = data["name"]
        login = data["login"]
        password = data.get("password", None)
        return cls(name, login, password)
