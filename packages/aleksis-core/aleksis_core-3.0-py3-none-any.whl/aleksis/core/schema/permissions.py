import graphene


class GlobalPermissionType(graphene.ObjectType):
    name = graphene.ID()
    result = graphene.Boolean()
