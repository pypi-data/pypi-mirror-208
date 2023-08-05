from typing import Union

from django.core.exceptions import PermissionDenied
from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from guardian.shortcuts import get_objects_for_user

from ..forms import PersonForm
from ..models import DummyPerson, Person
from ..util.core_helpers import get_site_preferences, has_person
from .base import FieldFileType
from .notification import NotificationType


class PersonPreferencesType(graphene.ObjectType):
    theme_design_mode = graphene.String()

    def resolve_theme_design_mode(parent, info, **kwargs):
        return parent["theme__design"]


class PersonType(DjangoObjectType):
    class Meta:
        model = Person
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "street",
            "housenumber",
            "postal_code",
            "place",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "photo",
            "avatar",
            "guardians",
            "primary_group",
            "description",
            "children",
            "owner_of",
            "member_of",
        ]

    full_name = graphene.String()
    username = graphene.String()
    userid = graphene.ID()
    photo = graphene.Field(FieldFileType)
    avatar = graphene.Field(FieldFileType)
    avatar_url = graphene.String()
    avatar_content_url = graphene.String()
    secondary_image_url = graphene.String()

    notifications = graphene.List(NotificationType)
    unread_notifications_count = graphene.Int()

    is_dummy = graphene.Boolean()
    preferences = graphene.Field(PersonPreferencesType)

    can_edit_person = graphene.Boolean()
    can_delete_person = graphene.Boolean()
    can_change_person_preferences = graphene.Boolean()
    can_impersonate_person = graphene.Boolean()
    can_invite_person = graphene.Boolean()

    def resolve_street(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_address_rule", root):
            return root.street
        return None

    def resolve_housenumber(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_address_rule", root):
            return root.housenumber
        return None

    def resolve_postal_code(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_address_rule", root):
            return root.postal_code
        return None

    def resolve_place(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_address_rule", root):
            return root.place
        return None

    def resolve_phone_number(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_contact_details_rule", root):
            return root.phone_number
        return None

    def resolve_mobile_number(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_contact_details_rule", root):
            return root.mobile_number
        return None

    def resolve_email(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_contact_details_rule", root):
            return root.email
        return None

    def resolve_date_of_birth(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return root.date_of_birth
        return None

    def resolve_place_of_birth(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return root.place_of_birth
        return None

    def resolve_children(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return get_objects_for_user(info.context.user, "core.view_person", root.children.all())
        return []

    def resolve_guardians(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_personal_details_rule", root):
            return get_objects_for_user(info.context.user, "core.view_person", root.guardians.all())
        return []

    def resolve_member_of(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_person_groups_rule", root):
            return get_objects_for_user(info.context.user, "core.view_group", root.member_of.all())
        return []

    def resolve_owner_of(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_person_groups_rule", root):
            return get_objects_for_user(info.context.user, "core.view_group", root.owner_of.all())
        return []

    def resolve_primary_group(root, info, **kwargs):  # noqa
        if info.context.user.has_perm("core.view_group_rule", root.primary_group):
            return root.primary_group
        raise PermissionDenied()

    def resolve_username(root, info, **kwargs):  # noqa
        return root.user.username if root.user else None

    def resolve_userid(root, info, **kwargs):  # noqa
        return root.user.id if root.user else None

    def resolve_unread_notifications_count(root, info, **kwargs):  # noqa
        return root.unread_notifications_count

    def resolve_photo(root, info, **kwargs):
        if info.context.user.has_perm("core.view_photo_rule", root):
            return root.photo
        return None

    def resolve_avatar(root, info, **kwargs):
        if info.context.user.has_perm("core.view_avatar_rule", root):
            return root.avatar
        return None

    def resolve_avatar_url(root, info, **kwargs):
        if info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
            return root.avatar.url
        return root.identicon_url

    def resolve_avatar_content_url(root, info, **kwargs):  # noqa
        # Returns the url for the main image for a person, either the avatar, photo or identicon,
        # based on permissions and preferences
        if get_site_preferences()["account__person_prefer_photo"]:
            if info.context.user.has_perm("core.view_photo_rule", root) and root.photo:
                return root.photo.url
            elif info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
                return root.avatar.url

        else:
            if info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
                return root.avatar.url
            elif info.context.user.has_perm("core.view_photo_rule", root) and root.photo:
                return root.photo.url

        return root.identicon_url

    def resolve_secondary_image_url(root, info, **kwargs):  # noqa
        # returns either the photo url or the avatar url,
        # depending on the one returned by avatar_content_url

        if get_site_preferences()["account__person_prefer_photo"]:
            if info.context.user.has_perm("core.view_avatar_rule", root) and root.avatar:
                return root.avatar.url
        elif info.context.user.has_perm("core.view_photo_rule", root) and root.photo:
            return root.photo.url
        return None

    def resolve_is_dummy(root: Union[Person, DummyPerson], info, **kwargs):
        return root.is_dummy if hasattr(root, "is_dummy") else False

    def resolve_notifications(root: Person, info, **kwargs):
        if has_person(info.context.user) and info.context.user.person == root:
            return root.notifications.filter(send_at__lte=timezone.now()).order_by(
                "read", "-created"
            )
        raise PermissionDenied()

    def resolve_can_edit_person(root, info, **kwargs):  # noqa
        return info.context.user.has_perm("core.edit_person_rule", root)

    def resolve_can_delete_person(root, info, **kwargs):  # noqa
        return info.context.user.has_perm("core.delete_person_rule", root)

    def resolve_can_change_person_preferences(root, info, **kwargs):  # noqa
        return info.context.user.has_perm("core.change_person_preferences_rule", root)

    def resolve_can_impersonate_person(root, info, **kwargs):  # noqa
        return root.user and info.context.user.has_perm("core.impersonate_rule", root)

    def resolve_can_invite_person(root, info, **kwargs):  # noqa
        return (not root.user) and info.context.user.has_perm("core.can_invite_rule", root)


class PersonMutation(DjangoModelFormMutation):
    person = graphene.Field(PersonType)

    class Meta:
        form_class = PersonForm

    @classmethod
    def perform_mutate(cls, form, info):
        if not form.initial:
            if not info.context.user.has_perm("core.create_person_rule"):
                raise PermissionDenied()
        else:
            if not info.context.user.has_perm("core.edit_person_rule", form.instance):
                raise PermissionDenied()
        return super().perform_mutate(form, info)
