from django.core.exceptions import PermissionDenied

import graphene
from graphene_django import DjangoObjectType

from ..models import Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = [
            "id",
            "sender",
            "recipient",
            "title",
            "description",
            "link",
            "icon",
            "send_at",
            "read",
            "sent",
            "created",
            "modified",
        ]

    @staticmethod
    def resolve_recipient(root, info, **kwargs):
        if info.context.user.has_perm("core.view_person_rule", root.recipient):
            return root.recipient
        raise PermissionDenied()


class MarkNotificationReadMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()  # noqa

    notification = graphene.Field(NotificationType)

    @classmethod
    def mutate(cls, root, info, id):  # noqa
        notification = Notification.objects.get(pk=id)

        if not info.context.user.has_perm("core.mark_notification_as_read_rule", notification):
            raise PermissionDenied()
        notification.read = True
        notification.save()

        return MarkNotificationReadMutation(notification=notification)
