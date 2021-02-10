from flask import Blueprint

admindash_blueprint = Blueprint('admindash', __name__)

from demabets.admindash import routes