from graphene_django import DjangoObjectType

from ..models import Room


class RoomType(DjangoObjectType):
    class Meta:
        model = Room
        fields = ("id", "name", "short_name")
