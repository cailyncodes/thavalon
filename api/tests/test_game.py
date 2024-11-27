import random
import unittest

from dal.game import GameDAL
from manager.game import GameManager
from model.person import Person
from model.role import Allegiance, RoleName


class TestNoDuplicateRolesWithVariableSeeds(unittest.TestCase):
  def setUp(self):
    """Set up game manager and persons for testing."""
    game_dal = GameDAL()
    self.game_manager = GameManager(game_dal)
    self.persons = [Person(f"Player{i}") for i in range(1, 11)]

  def test_no_duplicate_roles_with_variable_seeds(self):
    """Verify that no duplicate roles are assigned for different player counts with variable seeds."""
    test_cases = [(5, random.randint(0, 100000)) for _ in range(10000)] + \
           [(6, random.randint(0, 100000)) for _ in range(10000)] + \
           [(7, random.randint(0, 100000)) for _ in range(10000)] + \
           [(8, random.randint(0, 100000)) for _ in range(10000)] + \
           [(9, random.randint(0, 100000)) for _ in range(10000)] + \
           [(10, random.randint(0, 100000)) for _ in range(10000)]
    
    for num_players, seed in test_cases:
      with self.subTest(num_players=num_players, seed=seed):
        # Trim persons to match the number of players
        persons = self.persons[:num_players]
        
        # Set the random seed for deterministic behavior
        random.seed(seed)

        random_variant = random.choice(["thavalon", "jealousy", "esoteric"])
        
        # Assign roles using the game manager
        players = self.game_manager._assign_roles(persons, random_variant)
        
        # Extract role classes and check for duplicates
        roles = [player.role for player in players]
        role_names = [role.name for role in roles]
        
        self.assertEqual(
          len(roles), len(set(roles)),
          f"There should be no duplicate roles assigned in the game with {num_players} players and seed {seed}."
        )

        if num_players == 9 and RoleName.MERLIN in role_names:
          self.assertEqual(
            len([role for role in roles if role.allegiance == Allegiance.BAD]),
            4,
            "There should be 4 bad roles in a 9 players game with Merlin and seed {seed}."
          )
        if num_players == 9 and RoleName.MERLIN not in role_names:
          self.assertEqual(
            len([role for role in roles if role.allegiance == Allegiance.BAD]),
            3,
            "There should be 3 bad roles in a 9 players game without Merlin and seed {seed}."
          )
