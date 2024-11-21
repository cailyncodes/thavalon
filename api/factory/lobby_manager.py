"""
Factory class for LobbyManager, since we depend on the app object.
"""

from manager.lobby import LobbyManager


class LobbyManagerFactory:
    def __init__(self):
        self._lobby_manager = None

    def build(self, app) -> LobbyManager:
        if not self._lobby_manager:
            self._lobby_manager = LobbyManager(app)
        return self._lobby_manager
