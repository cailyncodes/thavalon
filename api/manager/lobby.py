"""
Manager class for the lobby.
"""

import asyncio
import hashlib
import random

from sanic import Sanic

from model.lobby import Lobby


class LobbyManager:
    """
    Manager class for the lobby.
    """

    lobbies: dict[str, Lobby] = None

    def __init__(self, app: Sanic):
        self.app = app
        self.lobbies = app.shared_ctx.lobbies

    # create lobby
    def create_lobby(self, name, persons) -> Lobby:
        """
        Create a lobby.
        """
        lobby_id = hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()
        lobby = Lobby.from_json(
            {"lobby_id": lobby_id, "name": name, "persons": persons}
        )
        self.lobbies.setdefault(lobby_id, lobby)
        return lobby

    # list all active lobbies
    def list_lobbies(self):
        """
        List all active lobbies.
        """
        return dict(
            filter(lambda entry: entry[1].status is not "closed", self.lobbies.items())
        )

    # get lobby by lobby id
    def get_lobby(self, lobby_id):
        """
        Get a lobby by lobby id.
        """
        return self.lobbies[lobby_id]

    # join lobby
    async def join_lobby(self, lobby_id, person):
        """
        Join a lobby.
        """
        # check the shared ctx value proxy lock, wait until it is False, but do not block the event loop
        while self.app.shared_ctx.locked.value:
            # do not block the event loop
            await asyncio.sleep(0.1)

        # set the shared ctx value proxy lock to True
        self.app.shared_ctx.locked.value = True

        lobby = self.lobbies[lobby_id]
        lobby.persons.append(person)
        self.lobbies.update({lobby_id: lobby})

        # set the shared ctx value proxy lock to False
        self.app.shared_ctx.locked.value = False
        return lobby

    # attach game
    async def attach_game(self, lobby_id, game_id):
        """
        Attach a game to a lobby.
        """
        # check the shared ctx value proxy lock, wait until it is False, but do not block the event loop
        while self.app.shared_ctx.locked.value:
            # do not block the event loop
            await asyncio.sleep(0.1)

        # set the shared ctx value proxy lock to True
        self.app.shared_ctx.locked.value = True

        lobby = self.lobbies[lobby_id]
        lobby.game_id = game_id
        lobby.status = "in-progress"
        self.lobbies.update({lobby_id: lobby})

        # set the shared ctx value proxy lock to False
        self.app.shared_ctx.locked.value = False
        return lobby

    # close lobby
    async def close_lobby(self, lobby_id):
        """
        Close a lobby.
        """
        # check the shared ctx value proxy lock, wait until it is False, but do not block the event loop
        while self.app.shared_ctx.locked.value:
            # do not block the event loop
            await asyncio.sleep(0.1)

        # set the shared ctx value proxy lock to True
        self.app.shared_ctx.locked.value = True

        lobby = self.lobbies[lobby_id]
        lobby.status = "closed"
        self.lobbies.update({lobby_id: lobby})

        # set the shared ctx value proxy lock to False
        self.app.shared_ctx.locked.value = False
        return lobby
