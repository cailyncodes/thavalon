"""
File for the stats view
"""

from base64 import b64decode

from model.mission import MissionVote
from model.person import Person
from model.proposal import ProposalVote
from sanic import Blueprint, response
from sanic.request import Request

from dal.game import GameDAL
from manager.game import GameManager

blueprint_game = Blueprint("game", url_prefix="/api/game")


# list games by status
@blueprint_game.route("/status", methods=["GET"])
async def list_games_by_status(request: Request):
  """
  List all games by status.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  games_map = game_manager.list_games_by_status()

  return response.json({status: [game.to_dict() for game in games] for (status, games) in games_map.items()})

# get game by game id
@blueprint_game.route("/<game_id>", methods=["GET"])
async def get_game(request: Request, game_id):
  """
  Get a game by game id.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
  game = game_manager.get_game(decoded_game_id)

  return response.json(game.to_dict())

# create game
@blueprint_game.route("/", methods=["POST"])
async def create_game(request: Request):
  """
  Create a game.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  # get persons from request
  persons = request.json.get("persons")
  if not persons:
    return response.json({"error": "Persons are required"}, status=400)

  # create game
  game = game_manager.create_game(persons)

  return response.json(game.to_dict())


# join game
@blueprint_game.route("/<game_id>/join", methods=["POST"])
async def join_game(request: Request, game_id):
  """
  Join a game.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
  person = request.json.get("person")
  if not person:
    return response.json({"error": "Person is required"}, status=400)

  try:
    game = game_manager.join_game(decoded_game_id, person)
    return response.json(game.to_dict())
  except Exception as e:
    return response.json({"error": str(e)}, status=500)
  
# assign roles and start game
@blueprint_game.route("/<game_id>/assign_roles_and_start", methods=["POST"])
async def assign_roles_and_start_game(request: Request, game_id):
  """
  Assign roles and start a game.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))

  variant = request.json.get("variant", "thavalon")

  try:
    game_manager.assign_roles_and_start_game(decoded_game_id, variant)
    return response.json({"message": "Game started successfully!"})
  except Exception as e:
    return response.json({"error": str(e)}, status=500)
  
# add proposal
@blueprint_game.route("/<game_id>/proposal", methods=["POST"])
async def add_proposal(request: Request, game_id):
  """
  Add a proposal.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
  proposer = Person.from_json({"name": request.json.get("proposer")})
  team = [Person.from_json(person) for person in request.json.get("team", [])]

  if not proposer:
    return response.json({"error": "Proposer is required"}, status=400)
  if not team:
    return response.json({"error": "Team is required"}, status=400)

  game = game_manager.add_proposal(decoded_game_id, proposer, team)

  return response.json(game.to_dict())

# add proposal vote
@blueprint_game.route("/<game_id>/proposal/vote", methods=["POST"])
async def add_proposal_vote(request: Request, game_id):
  """
  Add a proposal vote.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
  voter = Person.from_json({"name": request.json.get("voter")})
  option = ProposalVote.from_string(request.json.get("option"))
  if not voter:
    return response.json({"error": "Voter is required"}, status=400)
  if option is None:
    return response.json({"error": "Option is required"}, status=400)

  game = game_manager.add_proposal_vote(decoded_game_id, voter, option)

  return response.json(game.to_dict())

# add mission vote
@blueprint_game.route("/<game_id>/mission/vote", methods=["POST"])
async def add_mission_vote(request: Request, game_id):
  """
  Add a mission vote.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
  voter = Person.from_json({"name": request.json.get("voter")})
  vote = MissionVote.from_string(request.json.get("vote"))
  if not voter:
    return response.json({"error": "Voter is required"}, status=400)
  if vote is None:
    return response.json({"error": "Vote is required"}, status=400)

  game = game_manager.add_mission_vote(decoded_game_id, voter, vote)

  return response.json(game.to_dict())

# close game
@blueprint_game.route("/<game_id>/close", methods=["POST"])
async def close_game(request: Request, game_id):
  """
  Close a game.
  """
  game_dal = GameDAL()
  game_manager = GameManager(game_dal)
  decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
  game = game_manager.get_game(decoded_game_id)
  if not game:
    return response.json({"error": "Game not found"}, status=404)

  game_manager.close_game(decoded_game_id)

  return response.json({"message": "Game closed"})