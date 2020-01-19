from flask_socketio import SocketIO
from flask_cors import CORS

import api


app = api.create_app()
CORS(app)
socketio = SocketIO(app)

api.room.generate_sockets(socketio)

socketio.run(app, debug=True, host='0.0.0.0', port=80)
