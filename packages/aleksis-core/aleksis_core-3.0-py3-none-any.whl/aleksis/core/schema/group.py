from django.core.exceptions import PermissionDenied

from graphene_django import DjangoObjectType
from guardian.shortcuts import get_objects_for_user

from ..models import Group, Person
from ..util.core_helpers import has_person


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = [
            "id",
            "school_term",
            "name",
            "short_name",
            "members",
            "owners",
            "parent_groups",
            "group_type",
            "additional_fields",
            "photo",
            "avatar",
        ]

    @staticmethod
    def resolve_parent_groups(root, info, **kwargs):
        return get_objects_for_user(info.context.user, "core.view_group", root.parent_groups.all())

    @staticmethod
    def resolve_members(root, info, **kwargs):
        persons = get_objects_for_user(info.context.user, "core.view_person", root.members.all())
        if has_person(info.context.user) and [
            m for m in root.members.all() if m.pk == info.context.user.person.pk
        ]:
            persons = (persons | Person.objects.get(pk=info.context.user.person.pk)).distinct()
        return persons

    @staticmethod
    def resolve_owners(root, info, **kwargs):
        persons = get_objects_for_user(info.context.user, "core.view_person", root.owners.all())
        if has_person(info.context.user) and [
            o for o in root.owners.all() if o.pk == info.context.user.person.pk
        ]:
            persons = (persons | Person.objects.get(pk=info.context.user.person.pk)).distinct()
        return persons

    @staticmethod
    def resolve_group_type(root, info, **kwargs):
        if info.context.user.has_perm("core.view_grouptype_rule", root.group_type):
            return root.group_type
        raise PermissionDenied()

    @staticmethod
    def resolve_additional_fields(root, info, **kwargs):
        return get_objects_for_user(
            info.context.user, "core.view_additionalfield", root.additional_fields.all()
        )
