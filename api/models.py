from uuid import uuid4
import datetime

from mongoengine import Document
from mongoengine.fields import UUIDField, StringField, PointField, ImageField
from mongoengine.fields import ReferenceField, DateTimeField


class Room(Document):
    id = UUIDField(primary_key=True, default=lambda: uuid4())
    name = StringField(required=True)
    location = PointField(required=True)


class Message(Document):
    id = UUIDField(primary_key=True, default=lambda: uuid4())
    user = ReferenceField('User')
    room = ReferenceField('Room')
    message = StringField(max_length=500, required=True)
    timestamp = DateTimeField(required=True, default=lambda: datetime.datetime.now())
    location = PointField()


class User(Document):
    id = UUIDField(primary_key=True, default=lambda: uuid4())
    username = StringField(max_length=20, default=lambda: datetime.datetime.now())
    token = UUIDField(default=lambda: uuid4())
