"""
File for the stats view
"""

from sanic import Blueprint, response
from sanic.request import Request

from factory.lobby_manager import LobbyManagerFactory
from model.person import Person


blueprint_lobby = Blueprint("lobby", url_prefix="/api/lobby")

lobby_manager_factory = LobbyManagerFactory()


# create lobby
@blueprint_lobby.route("/", methods=["POST"])
async def create_lobby(request: Request):
    """
    Create a lobby.
    """
    # get name and players from request
    name = request.json.get("name")
    persons = request.json.get("persons")

    if not name or not persons:
        return response.json({"error": "Name and persons are required"}, status=400)

    lobby = lobby_manager_factory.build(request.app).create_lobby(name, persons)

    return response.json(lobby.to_dict())


# list all active lobbies
@blueprint_lobby.route("/", methods=["GET"])
async def list_lobbies(request: Request):
    """
    List all active lobbies.
    """
    lobbies = lobby_manager_factory.build(request.app).list_lobbies()
    lobbies = [lobby.to_dict() for lobby in lobbies.values()]
    return response.json({"lobbies": lobbies})


# get lobby by lobby id
@blueprint_lobby.route("/<lobby_id>", methods=["GET"])
async def get_lobby(request: Request, lobby_id):
    """
    Get a lobby by lobby id.
    """
    lobby = lobby_manager_factory.build(request.app).get_lobby(lobby_id)
    return response.json(lobby.to_dict())


# join lobby
@blueprint_lobby.route("/<lobby_id>/join", methods=["POST"])
async def join_lobby(request: Request, lobby_id):
    """
    Join a lobby.
    """
    # get person from request
    person_data = request.json.get("person")

    if not person_data:
        return response.json({"error": "Person is required"}, status=400)

    person = Person.from_json(person_data)

    lobby = await lobby_manager_factory.build(request.app).join_lobby(lobby_id, person)

    return response.json(lobby.to_dict())


# clear all lobbies
@blueprint_lobby.route("/clear", methods=["POST"])
async def clear_lobbies(request: Request):
    """
    Clear all lobbies.
    """
    lobby_manager = lobby_manager_factory.build(request.app)
    lobby_manager.lobbies.clear()
    lobby_manager.app.shared_ctx.locked.value = False
    return response.json({"message": "Lobbies cleared"})
