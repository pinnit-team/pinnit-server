from flask_socketio import SocketIO
from flask_cors import CORS

import api


app, socketio = api.create_app()

socketio.run(app, debug=True, host='0.0.0.0', port=80)
