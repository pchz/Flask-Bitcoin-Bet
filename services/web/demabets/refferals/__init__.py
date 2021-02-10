from flask import Blueprint

refferals_blueprint = Blueprint("refferals", __name__)

from demabets.refferals import routes
