import graphene

from .permissions import GlobalPermissionType
from .person import PersonType


class UserType(graphene.ObjectType):
    id = graphene.ID()  # noqa
    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()

    is_authenticated = graphene.Boolean(required=True)
    is_anonymous = graphene.Boolean(required=True)
    is_impersonate = graphene.Boolean()

    person = graphene.Field(PersonType)

    global_permissions_by_name = graphene.List(
        GlobalPermissionType, permissions=graphene.List(graphene.String)
    )

    def resolve_global_permissions_by_name(root, info, permissions, **kwargs):
        return [
            {"name": permission_name, "result": info.context.user.has_perm(permission_name)}
            for permission_name in permissions
        ]
