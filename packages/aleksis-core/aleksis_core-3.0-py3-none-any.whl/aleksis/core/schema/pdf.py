from django.core.exceptions import PermissionDenied

import graphene
from graphene_django import DjangoObjectType

from ..models import PDFFile
from .base import FieldFileType


class PDFFileType(DjangoObjectType):
    file = graphene.Field(FieldFileType)

    class Meta:
        model = PDFFile
        exclude = ["html_file"]

    @staticmethod
    def resolve_person(root, info, **kwargs):
        if info.context.user.has_perm("core.view_person_rule", root.person):
            return root.person
        raise PermissionDenied()
