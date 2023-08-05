import graphene
from graphene_django import DjangoObjectType

from aleksis.core.models import OAuthAccessToken, OAuthApplication

from .base import FieldFileType


class OAuthScope(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()


class OAuthApplicationType(DjangoObjectType):
    icon = graphene.Field(FieldFileType)

    class Meta:
        model = OAuthApplication
        fields = ["id", "name", "icon"]


class OAuthAccessTokenType(DjangoObjectType):
    scopes = graphene.List(OAuthScope)

    @staticmethod
    def resolve_scopes(root: OAuthAccessToken, info, **kwargs):
        return [OAuthScope(name=key, description=value) for key, value in root.scopes.items()]

    class Meta:
        model = OAuthAccessToken
        fields = ["id", "application", "expires", "created", "updated"]


class OAuthRevokeTokenMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()  # noqa

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id):  # noqa
        token = OAuthAccessToken.objects.get(id=id, user=info.context.user)
        token.delete()
        return OAuthRevokeTokenMutation(ok=True)
