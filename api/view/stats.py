"""
File for the stats view
"""

from sanic import Blueprint, response
from sanic.request import Request

from dal.stats import StatsDAL

blueprint_stats = Blueprint("stats", url_prefix="/api/stats")


@blueprint_stats.route("/", methods=["GET"])
async def get_stats(request: Request):
    """
    Get the stats.
    """
    stats_dal = StatsDAL()
    return response.json(stats_dal.get_stats())


@blueprint_stats.route("/", methods=["POST"])
async def update_stats(request: Request):
    """
    Update the stats.
    """
    stats_dal = StatsDAL()
    stats = request.json
    stats_dal.update_stats(stats)
    return response.json({"message": "Stats updated"})
