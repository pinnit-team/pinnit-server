from mongoengine import connect
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

from .room import ROOM_BP, generate_sockets


def create_app():
    socketio = SocketIO()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['DB'] = connect()

    CORS(app)

    app.register_blueprint(ROOM_BP)

    socketio.init_app(app, cors_allowed_origins='*')

    generate_sockets(socketio)


    return (app, socketio)
