from flask_socketio import SocketIO
from flask_cors import CORS

import api


app = api.create_app()
CORS(app)
socketio = SocketIO(app)

socketio.run(app, debug=True, host='0.0.0.0')
