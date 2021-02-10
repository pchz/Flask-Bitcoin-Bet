from flask import Blueprint

chat_blueprint = Blueprint("chat", __name__)

from demabets.chat import routes
