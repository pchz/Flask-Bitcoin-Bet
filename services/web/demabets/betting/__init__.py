from flask import Blueprint

betting_blueprint = Blueprint('betting', __name__)

from demabets.betting import routes