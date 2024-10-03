from flask import request
from src.http_server.session_handler import Session


def register_socket_events(socketio, session: Session):
    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        session.create_session(sid)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        session.end_session(sid)
