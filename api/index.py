"""
Entrypoint for the API server.
"""
from multiprocessing import Manager
import os

import sanic
from sanic_ext import Extend

from view.game import blueprint_game
from view.lobby import blueprint_lobby
from view.stats import blueprint_stats
from sanic.response import json

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_CHANNEL = "game_lobby"

app = sanic.Sanic(__name__)
app.config.EVENT_AUTOREGISTER = True
app.config.CORS_ORIGINS = "*"
Extend(app)

app.blueprint(blueprint_stats)
app.blueprint(blueprint_lobby)
app.blueprint(blueprint_game)

@app.main_process_start
async def main_process_start(app: sanic.Sanic):
    print("Main process started")
    m = Manager()
    app.shared_ctx.lobbies = m.dict()
    app.shared_ctx.locked = m.Value("b", False)

@app.route("/")
async def index(request):
    """Health check."""
    return json({"message": "Hello, world!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 8000))
