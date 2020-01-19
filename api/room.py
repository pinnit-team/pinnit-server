from time import time

from flask import current_app, Blueprint, make_response, jsonify, request
from flask_socketio import join_room, leave_room
from mongoengine.errors import DoesNotExist

from .models import Room, User, Message


ROOM_BP = Blueprint('room', __name__, url_prefix='/rooms')


@ROOM_BP.route('/', methods=['GET'])
def get_rooms():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')

    if not lat or not lon:
        room_args = {}

    else:
        room_args = {
            'location__near': [float(lon), float(lat)],
            'location__max_distance': 500
        }

    if radius:
        room_args['location__max_distance'] = int(radius)

    rooms = Room.objects(**room_args)

    rooms_ret = []
    for room in rooms:
        messages = Message.objects(room=room)
        rooms_ret.append(
            {
                'id': str(room.id),
                'name': room.name,
                'loc': room.location.get('coordinates'),
                'users': len(messages.distinct('user')),
                'messages': len(messages)
            }
        )

    return make_response(jsonify(rooms_ret), 200)


@ROOM_BP.route('/', methods=['POST'])
def create_room():
    content = request.get_json()

    name = content.get('name', None)
    lat = content.get('lat', None)
    lon = content.get('lon', None)

    if name and lat and lon:
        # create room
        new_room = Room(name=name, location=[lon, lat])
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


def generate_sockets(socketio):
    @socketio.on('join')
    def on_join(data):
        username = data.get('username')
        room = data.get('room')

        try:
            room_check = Room.objects.get(id=room)

        except DoesNotExist:
            return send({'err': 'room does not exist'}, json=True)

        if token:
            try:
                user = User.objects.get(token=token)

            except DoesNotExist:
                return send({'err': 'invalid token'}, json=True)

        else:

            if not username or username == 'SERVER':
                return send({'err': 'invalid username'}, json=True)

            user = User(username=username)
            user.save()

        message_history = Message.objects(room=room)

        join_room(room)

        send(
            {
                'userId': str(user.id),
                'token': str(user.token),
                'room': str(room_check.name),
                'history': [
                    {
                        'from': {
                            'id': str(user.id),
                            'username': user.username
                        },
                        'msg': message,
                        'attachment': attachment,
                        'timestamp': message.timestamp
                    } for i in message_history
                ],
                'err': None
            },
            json=True
        )

        send(
            {
                'user': {
                    'id': str(user.id),
                    'username': user.username
                },
                'msg': username + ' has entered the room.',
                'timestamp': time.time()
            },
            json=True,
            room=room
        )

    @socketio.on('leave')
    def on_leave(data):
        room = data.get('room')
        token = data.get('token')

        try:
            user = User.objects.get(token=token)
            leave_room(room)
            emit('leave',
                {
                    'user': {
                        'id': str(user.id),
                        'username': user.username
                    },
                    'msg': user.name + ' has left the room',
                    'timestamp': time.time()
                },
                room=room
            )

        except DoesNotExist:
            pass


    @socketio.on('sendmsg')
    def on_msg(data):
        token = data.get('token')
        room = data.get('room')
        message = data.get('msg')
        attachment = data.get('attachment')

        try:
            user = User.objects.get(token=token)
            room = Room.objects.get(id=room)

            message = Message(
                user=user,
                room=room,
                message=message,
                attachment=attachment
            )
            message.save()

            emit(
                'sendmsg',
                {
                    'from': {
                        'id': str(user.id),
                        'username': user.username
                    },
                    'msg': message,
                    'attachment': attachment,
                    'timestamp': message.timestamp
                },
                room=room
            )

        except DoesNotExist:
            pass
