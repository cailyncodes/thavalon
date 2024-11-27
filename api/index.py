"""
Entrypoint for the API server.
"""
import os
from multiprocessing import Manager

import sanic
from sanic.response import json
from sanic_ext import Extend

from util.word import get_top_common_words
from view.game import blueprint_game
from view.stats import blueprint_stats

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_CHANNEL = "game_lobby"

app = sanic.Sanic(__name__)
app.config.EVENT_AUTOREGISTER = True
app.config.CORS_ORIGINS = "*"
Extend(app)

app.blueprint(blueprint_stats)
app.blueprint(blueprint_game)

@app.main_process_start
async def main_process_start(app: sanic.Sanic):
  print("Main process started")
  m = Manager()
  app.shared_ctx.lobbies = m.dict()
  app.shared_ctx.locked = m.Value("b", False)

@app.before_server_start
async def before_server_start(app: sanic.Sanic, loop):
  print("Before server start")
  get_top_common_words(500)

@app.route("/")
async def index(request):
  """Health check."""
  return json({"message": "Hello, world!"})

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=os.environ.get("PORT", 8000))
