"""
File for the stats view
"""

from base64 import b64decode
from sanic import Blueprint, response
from sanic.request import Request

from dal.game import GameDAL
from factory.lobby_manager import LobbyManagerFactory
from manager.game import GameManager

blueprint_game = Blueprint("game", url_prefix="/api/game")


# create game
@blueprint_game.route("/", methods=["POST"])
async def create_game(request: Request):
    """
    Create a game.
    """
    game_dal = GameDAL()
    game_manager = GameManager(game_dal)
    # get lobby id from request
    lobby_id = request.json.get("lobby_id")
    if not lobby_id:
        return response.json({"error": "Lobby id is required"}, status=400)
    # look up lobby
    lobby_manager = LobbyManagerFactory().build(request.app)
    lobby = lobby_manager.get_lobby(lobby_id)
    if not lobby:
        return response.json({"error": "Lobby not found"}, status=404)

    # create game
    game = game_manager.create_game(lobby.persons)

    await lobby_manager.attach_game(lobby_id, game.id)

    return response.json(game.to_dict())


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


# close game
@blueprint_game.route("/<game_id>/close", methods=["POST"])
async def close_game(request: Request, game_id):
    """
    Close a game.
    """
    lobby_manager = LobbyManagerFactory().build(request.app)
    decoded_game_id = str(int(b64decode(game_id).decode("utf-8"), base=16))
    lobby = next(
        filter(
            lambda lobby: str(lobby.game_id) == decoded_game_id,
            lobby_manager.list_lobbies().values(),
        )
    )
    if lobby is None:
        return response.json({"error": "Game not found"}, status=404)

    await lobby_manager.close_lobby(lobby.lobby_id)

    return response.json({"message": "Game closed"})
