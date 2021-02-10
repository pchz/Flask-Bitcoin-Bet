from flask import Blueprint

profile_blueprint = Blueprint("profile", __name__)

from demabets.profile import routes
