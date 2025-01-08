# game_view.py

"""
File for the game view using Sanic
"""

from base64 import b64decode
from typing import List, Optional

from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import json

from model.mission import MissionVote
from model.person import Person
from model.proposal_vote import ProposalVote
from dal.game_dal import GameDAL
from manager.game import GameManager  # Ensure this is properly defined
import uuid
import asyncio

blueprint_game = Blueprint("game", url_prefix="/api/game")

dal = GameDAL()

# Helper function to run synchronous GameDAL methods in executor
async def run_sync(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


# 1. List games by status
@blueprint_game.route("/status", methods=["GET"])
async def list_games_by_status(request: Request):
    """
    Endpoint to list all games categorized by their status.
    """
    try:
        games = await run_sync(dal.list_games_by_status)
        games_serialized = {}
        for status, game_list in games.items():
            games_serialized[status] = [game.to_dict() for game in game_list]
        return json(games_serialized, status=200)
    except Exception as e:
        return json({"error": str(e)}, status=500)


# 2. Create a new game
@blueprint_game.route("/", methods=["POST"])
async def create_game(request: Request):
    """
    Endpoint to create a new game.
    Expected JSON Payload:
    {
        "name": "Epic Quest",
        "persons": ["Alice", "Bob", "Charlie", "Dave", "Eve"],
        "variant": "standard"  # Optional
    }
    """
    data = request.json
    name = data.get('name')
    persons_names = data.get('persons')
    variant = data.get('variant', 'thavalon')

    if not name or not persons_names:
        return json({"error": "Missing 'name' or 'persons' in request."}, status=400)

    # Validate that persons_names is a list of strings
    if not isinstance(persons_names, list) or not all(isinstance(name, str) for name in persons_names):
        return json({"error": "'persons' must be a list of strings."}, status=400)

    # Create Person and Player instances
    persons = [Person(name=name) for name in persons_names]
    players = [Player(person=person, role=None) for person in persons]

    # Initialize Game
    game = Game(
        name=name,
        persons=persons,
        players=players,
        status="in-progress",
        variant=variant
    )

    try:
        await run_sync(dal.create_game, game)
        return json({"message": "Game created successfully.", "game_id": str(game.id)}, status=201)
    except FileExistsError:
        return json({"error": "Game with this ID already exists."}, status=409)
    except TimeoutError:
        return json({"error": "Could not acquire lock to create game."}, status=503)
    except Exception as e:
        return json({"error": str(e)}, status=500)


# 3. Retrieve game details
@blueprint_game.route("/<game_id>", methods=["GET"])
async def get_game_details(request: Request, game_id: str):
    """
    Endpoint to retrieve details of a specific game by its ID.
    """
    try:
        # Validate and decode game_id if necessary
        # Assuming game_id is a UUID string
        try:
            uuid_obj = uuid.UUID(game_id)
        except ValueError:
            return json({"error": "Invalid game ID format."}, status=400)

        game = await run_sync(dal.get_game, game_id)
        if not game:
            return json({"error": "Game not found."}, status=404)

        return json(game.to_dict(), status=200)
    except FileNotFoundError:
        return json({"error": "Game not found."}, status=404)
    except TimeoutError:
        return json({"error": "Could not acquire lock to read game."}, status=503)
    except Exception as e:
        return json({"error": str(e)}, status=500)


# 4. Add a proposal
@blueprint_game.route("/<game_id>/proposal", methods=["POST"])
async def add_proposal(request: Request, game_id: str):
    """
    Endpoint to add a new proposal to a game.
    Expected JSON Payload:
    {
        "proposer": "Alice",
        "team": ["Bob", "Charlie"]
    }
    """
    data = request.json
    proposer_name = data.get('proposer')
    team_names = data.get('team')

    if not proposer_name or not team_names:
        return json({"error": "Missing 'proposer' or 'team' in request."}, status=400)

    # Validate team_names
    if not isinstance(team_names, list) or not all(isinstance(name, str) for name in team_names):
        return json({"error": "'team' must be a list of strings."}, status=400)

    try:
        # Retrieve the game
        game = await run_sync(dal.get_game, game_id)
        if not game:
            return json({"error": "Game not found."}, status=404)

        # Find the proposer
        proposer = next((player.person for player in game.players if player.person.name == proposer_name), None)
        if not proposer:
            return json({"error": "Proposer not found in the game."}, status=400)

        # Find team members
        team = []
        for name in team_names:
            person = next((player.person for player in game.players if player.person.name == name), None)
            if not person:
                return json({"error": f"Team member '{name}' not found in the game."}, status=400)
            team.append(person)

        # Add the proposal using GameDAL
        await run_sync(dal.add_proposal, game_id, proposer, team)

        return json({"message": "Proposal added successfully."}, status=201)

    except FileNotFoundError:
        return json({"error": "Game not found."}, status=404)
    except TimeoutError:
        return json({"error": "Could not acquire lock to update game."}, status=503)
    except ValueError as ve:
        return json({"error": str(ve)}, status=400)
    except Exception as e:
        return json({"error": str(e)}, status=500)


# 5. Cast a proposal vote
@blueprint_game.route("/<game_id>/proposal_vote", methods=["POST"])
async def cast_proposal_vote(request: Request, game_id: str):
    """
    Endpoint to cast a vote on the current proposal.
    Expected JSON Payload:
    {
        "voter": "Bob",
        "vote": "Yes"  # or "No"
    }
    """
    data = request.json
    voter_name = data.get('voter')
    vote_option = data.get('vote')

    if not voter_name or not vote_option:
        return json({"error": "Missing 'voter' or 'vote' in request."}, status=400)

    # Validate vote_option
    try:
        vote = ProposalVote.from_string(vote_option)
    except ValueError:
        return json({"error": "Invalid vote option. Must be 'Yes' or 'No'."}, status=400)

    try:
        # Retrieve the game
        game = await run_sync(dal.get_game, game_id)
        if not game:
            return json({"error": "Game not found."}, status=404)

        # Find the voter
        voter = next((player.person for player in game.players if player.person.name == voter_name), None)
        if not voter:
            return json({"error": "Voter not found in the game."}, status=400)

        # Cast the vote using GameDAL
        await run_sync(dal.add_proposal_vote, game_id, voter, vote)

        return json({"message": "Vote cast successfully."}, status=200)

    except FileNotFoundError:
        return json({"error": "Game not found."}, status=404)
    except TimeoutError:
        return json({"error": "Could not acquire lock to update game."}, status=503)
    except ValueError as ve:
        return json({"error": str(ve)}, status=400)
    except Exception as e:
        return json({"error": str(e)}, status=500)


# 6. Cast a mission vote
@blueprint_game.route("/<game_id>/mission_vote", methods=["POST"])
async def cast_mission_vote(request: Request, game_id: str):
    """
    Endpoint to cast a vote on the current mission.
    Expected JSON Payload:
    {
        "voter": "Charlie",
        "vote": "Success"  # or "Fail", "Reverse", "Cancel"
    }
    """
    data = request.json
    voter_name = data.get('voter')
    vote_option = data.get('vote')

    if not voter_name or not vote_option:
        return json({"error": "Missing 'voter' or 'vote' in request."}, status=400)

    # Validate vote_option
    try:
        vote = MissionVote.from_string(vote_option)
    except KeyError:
        return json({"error": "Invalid vote option. Must be 'Success', 'Fail', 'Reverse', or 'Cancel'."}, status=400)

    try:
        # Retrieve the game
        game = await run_sync(dal.get_game, game_id)
        if not game:
            return json({"error": "Game not found."}, status=404)

        # Find the voter
        voter = next((player.person for player in game.players if player.person.name == voter_name), None)
        if not voter:
            return json({"error": "Voter not found in the game."}, status=400)

        # Cast the mission vote using GameDAL
        await run_sync(dal.add_mission_vote, game_id, voter, vote)

        return json({"message": "Mission vote cast successfully."}, status=200)

    except FileNotFoundError:
        return json({"error": "Game not found."}, status=404)
    except TimeoutError:
        return json({"error": "Could not acquire lock to update game."}, status=503)
    except ValueError as ve:
        return json({"error": str(ve)}, status=400)
    except Exception as e:
        return json({"error": str(e)}, status=500)


# 7. Additional Endpoints (Optional)

# You can add more endpoints as needed, such as:
# - Assigning roles to players
# - Retrieving mission results
# - Ending the game
# - etc.

