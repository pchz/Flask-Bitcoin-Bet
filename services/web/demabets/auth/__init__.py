from flask import Blueprint

auth_blueprint = Blueprint("auth", __name__)

from demabets.auth import routes
