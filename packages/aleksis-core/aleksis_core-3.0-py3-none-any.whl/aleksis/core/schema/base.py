from django.core.exceptions import PermissionDenied
from django.db.models import Model

import graphene
from graphene_django import DjangoObjectType

from ..util.core_helpers import queryset_rules_filter


class RulesObjectType(DjangoObjectType):
    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, queryset, info, perm):
        q = super().get_queryset(queryset, info)

        return queryset_rules_filter(info.context, q, perm)


class FieldFileType(graphene.ObjectType):
    url = graphene.String()
    absolute_url = graphene.String()

    def resolve_url(root, info, **kwargs):
        return root.url if root else ""

    def resolve_absolute_url(root, info, **kwargs):
        return info.context.build_absolute_uri(root.url) if root else ""


class DeleteMutation(graphene.Mutation):
    """Mutation to delete an object."""

    klass: Model = None
    permission_required: str = ""
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()  # noqa

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = cls.klass.objects.get(pk=kwargs["id"])
        if info.context.user.has_perm(cls.permission_required, obj):
            obj.delete()
            return cls(ok=True)
        else:
            raise PermissionDenied()
