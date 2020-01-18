from uuid import uuid4

from mongoengine import Document
from mongoengine.fields import UUIDField, StringField, PointField
from mongoengine.fields import ReferenceField


class Room(Document):
    id = UUIDField(primary_key=True, default=uuid4())
    name = StringField(required=True)
    location = PointField(required=True)


class Message(Document):
    id = UUIDField(primary_key=True, default=uuid4())
    user = ReferenceField('User')
    message = StringField(max_length=500, required=True)


class User(Document):
    id = UUIDField(primary_key=True, default=uuid4())
    username = StringField(max_length=20, required=True)
