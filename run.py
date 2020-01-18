from flask_socketio import SocketIO

import api


app = api.create_app()
socketio = SocketIO(app)

socketio.run(app, debug=True, host='0.0.0.0')
