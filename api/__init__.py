from mongoengine import connect
from flask import Flask, render_template

from .room import ROOM_BP


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['DB'] = connect()

    app.register_blueprint(ROOM_BP)

    return app
