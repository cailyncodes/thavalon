import unittest
from copy import deepcopy

from model.game import Game
from model.person import Person
from model.player import Player
from model.role import Allegiance, RoleName, ALL_ROLES


class TestRoleBehaviors(unittest.TestCase):
  def setUp(self):
    """
    Helper method to retrieve a role by its RoleName enum.
    """
    self.roles = {role.name: role for role in ALL_ROLES}

  def test_good_and_bad_roles(self):
    """Verify good and bad roles are correctly identified."""
    good_role_names = [
      RoleName.MERLIN,
      RoleName.PERCIVAL,
      RoleName.ISEULT,
      RoleName.TRISTAN,
      RoleName.TITANIA,
      RoleName.ARTHUR,
      RoleName.LANCELOT,
      RoleName.OLDER_SIBLING,
      RoleName.UNICORN,
    ]
    bad_role_names = [
      RoleName.MORDRED,
      RoleName.MORGANA,
      RoleName.MAELAGANT,
      RoleName.AGRAVAINE,
      RoleName.COLGREVANCE,
      RoleName.JEALOUS_EX,
      RoleName.POLITICIAN,
    ]

    for role_name in good_role_names:
      role = self.roles.get(role_name)
      self.assertIsNotNone(role, f"Role {role_name.value} should exist.")
      self.assertEqual(
        role.allegiance,
        Allegiance.GOOD,
        f"{role.name.value} should be GOOD.",
      )

    for role_name in bad_role_names:
      role = self.roles.get(role_name)
      self.assertIsNotNone(role, f"Role {role_name.value} should exist.")
      self.assertEqual(
        role.allegiance,
        Allegiance.BAD,
        f"{role.name.value} should be BAD.",
      )

  def test_percival_sees_merlin_and_morgana(self):
    """Verify Percival sees Merlin and Morgana."""
    # Test with both Merlin and Morgana in the game
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MERLIN]),
        Player(Person("Player2"), self.roles[RoleName.MORGANA]),
        Player(Person("Player3"), self.roles[RoleName.PERCIVAL]),
      ],
      persons=[],
    )
    percival = next(
      p for p in game.players if p.role.name == RoleName.PERCIVAL
    )
    information = percival.role.information(game)

    expected_messages = {
      "Player1 is Merlin or Morgana.",
      "Player2 is Merlin or Morgana.",
    }

    self.assertEqual(
      len(information),
      2,
      "Percival should see exactly Merlin and Morgana.",
    )
    for message in information:
      self.assertIn(
        message,
        expected_messages,
        f"Percival should see Merlin or Morgana: '{message}'",
      )

    # Test with only Merlin in the game
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MERLIN]),
        Player(Person("Player2"), self.roles[RoleName.PERCIVAL]),
      ],
      persons=[],
    )
    percival = next(
      p for p in game.players if p.role.name == RoleName.PERCIVAL
    )
    information = percival.role.information(game)

    expected_messages = {"Player1 is Merlin or Morgana."}

    self.assertEqual(
      len(information),
      1,
      "Percival should see only Merlin if Morgana is absent.",
    )
    self.assertIn(
      "Player1 is Merlin or Morgana.",
      information,
      "Percival should see Merlin.",
    )

  def test_merlin_sees_lancelot_and_bad_roles(self):
    """Verify Merlin sees Lancelot and all bad roles."""
    # Test with Lancelot and all bad roles
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MERLIN]),
        Player(Person("Player2"), self.roles[RoleName.LANCELOT]),
        Player(Person("Player3"), self.roles[RoleName.MORDRED]),
        Player(Person("Player4"), self.roles[RoleName.MORGANA]),
        Player(Person("Player5"), self.roles[RoleName.MAELAGANT]),
        Player(Person("Player6"), self.roles[RoleName.AGRAVAINE]),
      ],
      persons=[],
    )
    merlin = next(
      p for p in game.players if p.role.name == RoleName.MERLIN
    )
    information = merlin.role.information(game)

    expected_messages = {
      "Player2 is Evil.",
      "Player4 is Evil.",
      "Player5 is Evil.",
      "Player6 is Evil.",
    }

    self.assertEqual(
      len(information),
      4,
      "Merlin should see Lancelot and all bad roles.",
    )
    for message in information:
      self.assertIn(
        message,
        expected_messages,
        f"Merlin should see Lancelot and all bad roles: '{message}'",
      )

    # Test with only Lancelot in the game
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MERLIN]),
        Player(Person("Player2"), self.roles[RoleName.LANCELOT]),
      ],
      persons=[],
    )
    merlin = next(
      p for p in game.players if p.role.name == RoleName.MERLIN
    )
    information = merlin.role.information(game)

    self.assertEqual(
      len(information),
      1,
      "Merlin should see only Lancelot if no bad roles are present.",
    )
    self.assertIn(
      "Player2 is Evil.",
      information,
      "Merlin should see Lancelot.",
    )

  def test_iseult_and_tristan_pairing(self):
    """Verify Iseult and Tristan are always both in the game or both not."""
    # Test with both Iseult and Tristan
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.ISEULT]),
        Player(Person("Player2"), self.roles[RoleName.TRISTAN]),
      ],
      persons=[],
    )
    iseult_information = next(
      p.role.information(game) for p in game.players if p.role.name == RoleName.ISEULT
    )
    tristan_information = next(
      p.role.information(game) for p in game.players if p.role.name == RoleName.TRISTAN
    )
    self.assertEqual(
      len(iseult_information),
      1,
      "Iseult should see exactly one player.",
    )
    self.assertEqual(
      len(tristan_information),
      1,
      "Tristan should see exactly one player.",
    )
    self.assertIn(
      "Player2 is Tristan.",
      iseult_information,
      "Iseult should see Tristan.",
    )
    self.assertIn(
      "Player1 is Iseult.",
      tristan_information,
      "Tristan should see Iseult.",
    )

  def test_arthur_sees_good_roles(self):
    """Verify Arthur sees the set of good roles in the game (not the players)."""
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.ARTHUR]),
        Player(Person("Player2"), self.roles[RoleName.MERLIN]),
        Player(Person("Player3"), self.roles[RoleName.PERCIVAL]),
        Player(Person("Player4"), self.roles[RoleName.MORDRED]),
      ],
      persons=[],
    )
    arthur = next(
      p for p in game.players if p.role.name == RoleName.ARTHUR
    )
    information = arthur.role.information(game)
    self.assertIn(
      "Merlin",
      information,
      "Arthur should see Merlin.",
    )
    self.assertIn(
      "Percival",
      information,
      "Arthur should see Percival.",
    )
    self.assertNotIn(
      "Mordred",
      information,
      "Arthur should not see Mordred.",
    )
    self.assertNotIn(
      "Player4 is Evil.",
      information,
      "Arthur should not see bad roles.",
    )

  def test_lancelot_gets_no_information(self):
    """Verify Lancelot receives no information."""
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.LANCELOT]),
        Player(Person("Player2"), self.roles[RoleName.MERLIN]),
        Player(Person("Player3"), self.roles[RoleName.PERCIVAL]),
      ],
      persons=[],
    )
    lancelot = next(
      p for p in game.players if p.role.name == RoleName.LANCELOT
    )
    information = lancelot.role.information(game)
    self.assertEqual(
      len(information),
      0,
      "Lancelot should receive no information.",
    )

  def test_bad_roles_see_other_bad_roles_and_titania(self):
    """Verify all Bad roles see other bad players and Titania if present."""
    # Test with Titania present
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MORDRED]),
        Player(Person("Player2"), self.roles[RoleName.MORGANA]),
        Player(Person("Player3"), self.roles[RoleName.MAELAGANT]),
        Player(Person("Player4"), self.roles[RoleName.AGRAVAINE]),
        Player(Person("Player5"), self.roles[RoleName.TITANIA]),
      ],
      persons=[],
    )
    for player in game.players:
      if player.role.allegiance == Allegiance.BAD:
        information = player.role.information(game)
        # Ensure the player does not see themselves
        self.assertNotIn(
          player.person.name,
          "\n".join(information),
          "Bad role should not see themselves.",
        )
        # Check visibility of other bad roles
        for other_player in game.players:
          if (
            other_player.role.allegiance == Allegiance.BAD
            and other_player.person.name != player.person.name
          ):
            expected_message = (
              f"{other_player.person.name} is Evil."
              if other_player.role.name != RoleName.COLGREVANCE
              else f"{other_player.person.name} is {other_player.role.name.value}."
            )
            self.assertIn(
              expected_message,
              information,
              f"Bad role should see {other_player.role.name.value}.",
            )
        # Check for Titania's infiltration message
        self.assertIn(
          "Titania infiltrated your ranks.",
          information,
          "Bad role should see Titania infiltrated your ranks.",
        )

    # Test with Titania absent
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MORDRED]),
        Player(Person("Player2"), self.roles[RoleName.MORGANA]),
        Player(Person("Player3"), self.roles[RoleName.MAELAGANT]),
        Player(Person("Player4"), self.roles[RoleName.AGRAVAINE]),
      ],
      persons=[],
    )
    for player in game.players:
      if player.role.allegiance == Allegiance.BAD:
        information = player.role.information(game)
        # Ensure the player does not see themselves
        self.assertNotIn(
          player.person.name,
          "\n".join(information),
          "Bad role should not see themselves.",
        )
        # Check visibility of other bad roles
        for other_player in game.players:
          if (
            other_player.role.allegiance == Allegiance.BAD
            and other_player.person.name != player.person.name
          ):
            expected_message = (
              f"{other_player.person.name} is Evil."
              if other_player.role.name != RoleName.COLGREVANCE
              else f"{other_player.person.name} is {other_player.role.name.value}."
            )
            self.assertIn(
              expected_message,
              information,
              f"Bad role should see {other_player.role.name.value}.",
            )
        # Ensure Titania's infiltration message is not present
        self.assertNotIn(
          "Titania infiltrated your ranks.",
          information,
          "Bad role should not see Titania's infiltration message when Titania is absent.",
        )

  def test_colgrevance_does_not_see_titania(self):
    """Verify Colgrevance does not see Titania."""
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.COLGREVANCE]),
        Player(Person("Player2"), self.roles[RoleName.MORDRED]),
        Player(Person("Player3"), self.roles[RoleName.MORGANA]),
        Player(Person("Player4"), self.roles[RoleName.MAELAGANT]),
        Player(Person("Player5"), self.roles[RoleName.TITANIA]),
      ],
      persons=[],
    )
    colgrevance = next(
      p for p in game.players if p.role.name == RoleName.COLGREVANCE
    )
    information = colgrevance.role.information(game)

    # Colgrevance should not see Titania
    self.assertNotIn(
      "Player5 is Colgrevance.",
      information,
      "Colgrevance should not see themselves.",
    )
    self.assertNotIn(
      "Titania infiltrated your ranks.",
      information,
      "Colgrevance should not see Titania infiltrated your ranks.",
    )
    # Check visibility of other bad roles
    self.assertIn("Player2 is Mordred.", information, "Colgrevance should see Mordred.")
    self.assertIn("Player3 is Morgana.", information, "Colgrevance should see Morgana.")
    self.assertIn("Player4 is Maelagant.", information, "Colgrevance should see Maelagant.")

  def test_jealous_ex_sees_older_sibling_or_lovers(self):
    """Verify Jealous Ex sees either the Older Sibling or both Iseult and Tristan."""
    # Case 1: Jealous Ex sees Older Sibling
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.JEALOUS_EX]),
        Player(Person("Player2"), self.roles[RoleName.OLDER_SIBLING]),
      ],
      persons=[],
    )
    jealous_ex = next(
      p for p in game.players if p.role.name == RoleName.JEALOUS_EX
    )
    information = jealous_ex.role.information(game)

    expected_messages = {"Player2 is Iseult or the Older Sibling."}

    self.assertEqual(
      len(information),
      1,
      "Jealous Ex should see exactly one player in this case.",
    )
    self.assertIn(
      "Player2 is Iseult or the Older Sibling.",
      information,
      "Jealous Ex should see Older Sibling.",
    )

    # Case 2: Jealous Ex sees both Iseult and Tristan (the lovers)
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.JEALOUS_EX]),
        Player(Person("Player2"), self.roles[RoleName.ISEULT]),
        Player(Person("Player3"), self.roles[RoleName.TRISTAN]),
      ],
      persons=[],
    )
    jealous_ex = next(
      p for p in game.players if p.role.name == RoleName.JEALOUS_EX
    )
    information = jealous_ex.role.information(game)

    expected_messages = {
      "Player2 is Iseult or the Older Sibling.",
    }

    self.assertEqual(
      len(information),
      1,
      "Jealous Ex should see exactly one player in this case.",
    )
    for message in information:
      self.assertIn(
        message,
        expected_messages,
        f"Jealous Ex should see Iseult or Tristan: '{message}'",
      )

    # Case 3: No valid target for Jealous Ex
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.JEALOUS_EX]),
        Player(Person("Player2"), self.roles[RoleName.MORDRED]),
      ],
      persons=[],
    )
    jealous_ex = next(
      p for p in game.players if p.role.name == RoleName.JEALOUS_EX
    )
    information = jealous_ex.role.information(game)

    self.assertEqual(
      len(information),
      1,
      "Jealous Ex should see no one (except evil players) if neither Older Sibling nor lovers are in the game.",
    )

  def test_unicorn_sees_lovers_or_older_sibling_and_mordred(self):
    """Verify Unicorn sees the lovers, the Older Sibling, and Mordred if they are in the game."""
    # Case 1: Sees the lovers and Mordred
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.UNICORN]),
        Player(Person("Player2"), self.roles[RoleName.ISEULT]),
        Player(Person("Player3"), self.roles[RoleName.TRISTAN]),
        Player(Person("Player4"), self.roles[RoleName.MORDRED]),
      ],
      persons=[],
    )
    unicorn = next(
      p for p in game.players if p.role.name == RoleName.UNICORN
    )
    information = unicorn.role.information(game)

    expected_messages = {
      "Player2 is Tristan or Iseult or Older Sibling or Mordred.",
      "Player3 is Tristan or Iseult or Older Sibling or Mordred.",
      "Player4 is Tristan or Iseult or Older Sibling or Mordred.",
    }

    self.assertEqual(
      len(information),
      3,
      "Unicorn should see exactly three players in this case.",
    )
    for message in information:
      self.assertIn(
        message,
        expected_messages,
        f"Unicorn should see the correct roles: '{message}'",
      )

    # Case 2: Sees the Older Sibling and Mordred
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.UNICORN]),
        Player(Person("Player2"), self.roles[RoleName.OLDER_SIBLING]),
        Player(Person("Player3"), self.roles[RoleName.MORDRED]),
      ],
      persons=[],
    )
    unicorn = next(
      p for p in game.players if p.role.name == RoleName.UNICORN
    )
    information = unicorn.role.information(game)

    expected_messages = {
      "Player2 is Tristan or Iseult or Older Sibling or Mordred.",
      "Player3 is Tristan or Iseult or Older Sibling or Mordred.",
    }

    self.assertEqual(
      len(information),
      2,
      "Unicorn should see exactly two players in this case.",
    )
    for message in information:
      self.assertIn(
        message,
        expected_messages,
        f"Unicorn should see the correct roles: '{message}'",
      )

    # Case 3: Sees only Mordred
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.UNICORN]),
        Player(Person("Player2"), self.roles[RoleName.MORDRED]),
      ],
      persons=[],
    )
    unicorn = next(
      p for p in game.players if p.role.name == RoleName.UNICORN
    )
    information = unicorn.role.information(game)

    expected_messages = {
      "Player2 is Tristan or Iseult or Older Sibling or Mordred.",
    }

    self.assertEqual(
      len(information),
      1,
      "Unicorn should see exactly one player in this case.",
    )
    self.assertIn(
      "Player2 is Tristan or Iseult or Older Sibling or Mordred.",
      information,
      "Unicorn should see Mordred.",
    )

    # Case 4: Sees no one
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.UNICORN]),
      ],
      persons=[],
    )
    unicorn = next(
      p for p in game.players if p.role.name == RoleName.UNICORN
    )
    information = unicorn.role.information(game)

    self.assertEqual(
      len(information),
      0,
      "Unicorn should see no one if neither lovers, Older Sibling, nor Mordred are in the game.",
    )

  def test_bad_roles_do_not_see_themselves(self):
    """Verify that bad roles do not see themselves."""
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.MORDRED]),
        Player(Person("Player2"), self.roles[RoleName.MORGANA]),
        Player(Person("Player3"), self.roles[RoleName.MAELAGANT]),
        Player(Person("Player4"), self.roles[RoleName.AGRAVAINE]),
      ],
      persons=[],
    )
    for player in game.players:
      if player.role.allegiance == Allegiance.BAD:
        information = player.role.information(game)
        # Ensure the player does not see themselves
        self.assertNotIn(
          f"{player.person.name} is Evil.",
          information,
          "Bad role should not see themselves as Evil.",
        )
        # Ensure Titania's infiltration message is not present since Titania is absent
        self.assertNotIn(
          "Titania infiltrated your ranks.",
          information,
          "Bad role should not see Titania's infiltration message when Titania is absent.",
        )
        # Check visibility of other bad roles
        for other_player in game.players:
          if (
            other_player.role.allegiance == Allegiance.BAD
            and other_player.person.name != player.person.name
          ):
            expected_message = (
              f"{other_player.person.name} is Evil."
              if other_player.role.name != RoleName.COLGREVANCE
              else f"{other_player.person.name} is {other_player.role.name.value}."
            )
            self.assertIn(
              expected_message,
              information,
              f"Bad role should see {other_player.role.name.value}.",
            )
      
  def test_nimue_sees_all_roles(self):
    """Verify Nimue sees all roles in the game."""
    game = Game(
      name="Test Game",
      players=[
        Player(Person("Player1"), self.roles[RoleName.NIMUE]),
        Player(Person("Player2"), self.roles[RoleName.MERLIN]),
        Player(Person("Player3"), self.roles[RoleName.PERCIVAL]),
        Player(Person("Player4"), self.roles[RoleName.MORDRED]),
        Player(Person("Player5"), self.roles[RoleName.MORGANA]),
      ],
      persons=[],
    )

    nimue = next(
      p for p in game.players if p.role.name == RoleName.NIMUE
    )

    information = nimue.role.information(game)

    expected_messages = {
      "Merlin",
      "Morgana",
      "Mordred",
      "Percival",
    }

    self.assertEqual(
      len(information),
      4,
      "Nimue should see all roles in the game.",
    )

    for message in information:
      self.assertIn(
        message,
        expected_messages,
        f"Nimue should see all roles: '{message}'",
      )


if __name__ == "__main__":
  unittest.main()
