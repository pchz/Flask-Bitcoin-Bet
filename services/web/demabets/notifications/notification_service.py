from demabets.notifications import notifications_blueprint
from demabets import socketio


def send_notification(title, message):
    socketio.emit('notification', {
        'title': title,
        'message': message,
    }, broadcast=True)
