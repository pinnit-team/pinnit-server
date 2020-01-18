from flask import current_app, Blueprint, make_response, jsonify, request

from .models import Room


ROOM_BP = Blueprint('room', __name__, url_prefix='/rooms')


@ROOM_BP.route('/', methods=['GET'])
def get_rooms():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not lat or not lon:
        return 400

    rooms = Room.objects(
        location__near=[float(lat), float(lon)],
        location__max_distance=500
    )

    rooms_ret = {
        str(i.id): {
            'name': i.name, 'loc': i.location.get('coordinates')
        } for i in rooms
    }

    return make_response(jsonify(rooms_ret), 200)


@ROOM_BP.route('/', methods=['POST'])
def create_room():
    content = request.get_json()

    name = content.get('name', None)
    lat = content.get('lat', None)
    lon = content.get('lon', None)

    if name and lat and lon:
        # create room
        new_room = Room(name=name, location=[lat, lon])
        new_room.save()

        return make_response(
            jsonify(
                {'room':
                    {'name': new_room.name,
                     'location': new_room.location
                    },
                 'err': None
                }
            ),
            200
        )

    else:
        return make_response(
            jsonify({'room': None, 'err': 'missing fields'}),
            400
        )
