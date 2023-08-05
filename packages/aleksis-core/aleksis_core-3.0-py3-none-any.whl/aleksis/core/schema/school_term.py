from graphene_django import DjangoObjectType

from ..models import SchoolTerm


class SchoolTermType(DjangoObjectType):
    class Meta:
        model = SchoolTerm
