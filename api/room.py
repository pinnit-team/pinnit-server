import datetime
from html import escape

from flask import current_app, Blueprint, make_response, jsonify, request
from flask_socketio import join_room, leave_room, send, emit
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
            'location__max_distance': 100
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
                'users': [i.location.get('coordinates') for i in Message.objects(room=room).order_by('-timestamp')],
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
        new_room = Room(name=escape(name[:20]), location=[lon, lat])
        new_room.save()

        return make_response(
            jsonify(
                {'room':
                    {'name': new_room.name,
                     'id': str(new_room.id),
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
    def on_join(json):
        username = json.get('username')
        room = json.get('room')
        token = json.get('token')

        print(json)

        try:
            room_check = Room.objects.get(id=room)

        except DoesNotExist:
            return emit('join', {'err': 'room does not exist'}, broadcast=False)

        if token:
            try:
                user = User.objects.get(token=token)

            except DoesNotExist:
                return send({'err': 'invalid token'}, json=True)

        else:

            if not username or username == 'SERVER':
                return send({'err': 'invalid username'}, json=True)

            user = User(username=escape(username[:20]))
            user.save()

        message_history = Message.objects(room=room)

        join_room(room)

        emit('join-private',
            {
                'userId': str(user.id),
                'token': str(user.token),
                'room': str(room_check.name),
                'history': [
                    {
                        'from': {
                            'id': str(i.user.id),
                            'username': i.user.username
                        },
                        'msg': i.message,
                        'timestamp': str(i.timestamp)
                    } for i in message_history.order_by('+timestamp')
                ],
                'err': None
            },
            broadcast=False
        )

        emit(
            'join',
            {
                'user': {
                    'id': str(user.id),
                    'username': user.username
                },
                'msg': username + ' has entered the room.',
                'timestamp': str(datetime.datetime.now())
            },
            json=True,
            room=room
        )


    @socketio.on('leave')
    def on_leave(json):
        room = json.get('room')
        token = json.get('token')

        print(json)

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
                    'timestamp': str(datetime.datetime.now())
                },
                json=True,
                room=room
            )

        except DoesNotExist:
            pass


    @socketio.on('sendmsg')
    def on_msg(json):
        token = json.get('token')
        room = json.get('roomId')
        message = json.get('msg')
        location = json.get('location')

        print(json)

        try:
            user = User.objects.get(token=token)
            room = Room.objects.get(id=room)

            print(escape(message[:500]))
            message = Message(
                user=user,
                room=room,
                message=escape(message[:500]),
                location=[
                    float(location.get('longitude')),
                    float(location.get('latitude'))
                ]
            )
            message.save()

            emit(
                'sendmsg',
                {
                    'from': {
                        'id': str(user.id),
                        'username': user.username
                    },
                    'msg': message.message,
                    'timestamp': str(message.timestamp)
                },
                room=str(room.id),
                json=True
            )

        except DoesNotExist:
            pass
