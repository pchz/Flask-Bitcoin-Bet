from flask import Blueprint

frontpage_blueprint = Blueprint('frontpage', __name__)

from demabets.frontpage import routes