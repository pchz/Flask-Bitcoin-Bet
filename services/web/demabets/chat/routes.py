from flask_login import current_user
from flask_socketio import emit

from demabets import db
from demabets import socketio
from demabets.models import Chat
from demabets.utils import authenticated_only, RateLimiter


@socketio.on('message')
@authenticated_only
@RateLimiter(max_calls=10, period=1)
def handle_message(msg):
    message = Chat(message=msg['msg'], username=current_user.username)
    db.session.add(message)
    db.session.commit()

    emit('msg', {'author': current_user.username, 'msg': msg['msg']}, broadcast=True)
