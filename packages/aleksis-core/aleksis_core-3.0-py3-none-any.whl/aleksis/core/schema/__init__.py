from django.apps import apps
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q

import graphene
from guardian.shortcuts import get_objects_for_user
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from haystack.utils.loading import UnifiedIndex

from ..models import (
    CustomMenu,
    DynamicRoute,
    Notification,
    OAuthAccessToken,
    PDFFile,
    Person,
    TaskUserAssignment,
)
from ..util.apps import AppConfig
from ..util.core_helpers import get_allowed_object_ids, get_app_module, get_app_packages, has_person
from .celery_progress import CeleryProgressFetchedMutation, CeleryProgressType
from .custom_menu import CustomMenuType
from .dynamic_routes import DynamicRouteType
from .group import GroupType  # noqa
from .installed_apps import AppType
from .message import MessageType
from .notification import MarkNotificationReadMutation, NotificationType
from .oauth import OAuthAccessTokenType, OAuthRevokeTokenMutation
from .pdf import PDFFileType
from .person import PersonMutation, PersonType
from .school_term import SchoolTermType  # noqa
from .search import SearchResultType
from .system_properties import SystemPropertiesType
from .two_factor import TwoFactorType
from .user import UserType


class Query(graphene.ObjectType):
    ping = graphene.String(payload=graphene.String())

    notifications = graphene.List(NotificationType)

    persons = graphene.List(PersonType)
    person_by_id = graphene.Field(PersonType, id=graphene.ID())
    person_by_id_or_me = graphene.Field(PersonType, id=graphene.ID())

    who_am_i = graphene.Field(UserType)

    system_properties = graphene.Field(SystemPropertiesType)
    installed_apps = graphene.List(AppType)

    celery_progress_by_task_id = graphene.Field(CeleryProgressType, task_id=graphene.String())
    celery_progress_by_user = graphene.List(CeleryProgressType)

    pdf_by_id = graphene.Field(PDFFileType, id=graphene.ID())

    search_snippets = graphene.List(
        SearchResultType, query=graphene.String(), limit=graphene.Int(required=False)
    )

    messages = graphene.List(MessageType)

    custom_menu_by_name = graphene.Field(CustomMenuType, name=graphene.String())

    dynamic_routes = graphene.List(DynamicRouteType)

    two_factor = graphene.Field(TwoFactorType)

    oauth_access_tokens = graphene.List(OAuthAccessTokenType)

    def resolve_ping(root, info, payload) -> str:
        return payload

    def resolve_notifications(root, info, **kwargs):
        return Notification.objects.filter(
            Q(
                pk__in=get_objects_for_user(
                    info.context.user, "core.view_person", Person.objects.all()
                )
            )
            | Q(recipient=info.context.user.person)
        )

    def resolve_persons(root, info, **kwargs):
        return get_objects_for_user(info.context.user, "core.view_person", Person.objects.all())

    def resolve_person_by_id(root, info, id):  # noqa
        person = Person.objects.get(pk=id)
        if not info.context.user.has_perm("core.view_person_rule", person):
            raise PermissionDenied()
        return person

    def resolve_person_by_id_or_me(root, info, **kwargs):  # noqa
        # Returns person associated with current user if id is None, else the person with the id
        if "id" not in kwargs or kwargs["id"] is None:
            return info.context.user.person if has_person(info.context.user) else None

        person = Person.objects.get(pk=kwargs["id"])
        if not info.context.user.has_perm("core.view_person_rule", person):
            raise PermissionDenied()
        return person

    def resolve_who_am_i(root, info, **kwargs):
        return info.context.user

    def resolve_system_properties(root, info, **kwargs):
        return True

    def resolve_installed_apps(root, info, **kwargs):
        return [app for app in apps.get_app_configs() if isinstance(app, AppConfig)]

    def resolve_celery_progress_by_task_id(root, info, task_id, **kwargs):
        task = TaskUserAssignment.objects.get(task_result__task_id=task_id)

        if not info.context.user.has_perm("core.view_progress_rule", task):
            raise PermissionDenied()
        progress = task.get_progress_with_meta()
        return progress

    def resolve_celery_progress_by_user(root, info, **kwargs):
        if info.context.user.is_anonymous:
            return None
        tasks = TaskUserAssignment.objects.filter(user=info.context.user)
        return [
            task.get_progress_with_meta()
            for task in tasks
            if task.get_progress_with_meta()["complete"] is False
        ]

    def resolve_pdf_by_id(root, info, id, **kwargs):  # noqa
        pdf_file = PDFFile.objects.get(pk=id)
        if has_person(info.context) and not info.context.user.person == pdf_file.person:
            raise PermissionDenied()
        return pdf_file

    def resolve_search_snippets(root, info, query, limit=-1, **kwargs):
        indexed_models = UnifiedIndex().get_indexed_models()
        allowed_object_ids = get_allowed_object_ids(info.context.user, indexed_models)

        if allowed_object_ids:
            results = (
                SearchQuerySet().filter(id__in=allowed_object_ids).filter(text=AutoQuery(query))
            )
            if limit < 0:
                return results
            return results[:limit]
        else:
            return None

    def resolve_messages(root, info, **kwargs):
        return get_messages(info.context)

    def resolve_custom_menu_by_name(root, info, name, **kwargs):
        return CustomMenu.get_default(name)

    def resolve_dynamic_routes(root, info, **kwargs):
        dynamic_routes = []

        for dynamic_route_object in DynamicRoute.registered_objects_dict.values():
            dynamic_routes += dynamic_route_object.get_dynamic_routes()

        return dynamic_routes

    def resolve_two_factor(root, info, **kwargs):
        if info.context.user.is_anonymous:
            return None
        return info.context.user

    @staticmethod
    def resolve_oauth_access_tokens(root, info, **kwargs):
        return OAuthAccessToken.objects.filter(user=info.context.user)


class Mutation(graphene.ObjectType):
    update_person = PersonMutation.Field()

    mark_notification_read = MarkNotificationReadMutation.Field()

    celery_progress_fetched = CeleryProgressFetchedMutation.Field()

    revoke_oauth_token = OAuthRevokeTokenMutation.Field()


def build_global_schema():
    """Build global GraphQL schema from all apps."""
    query_bases = [Query]
    mutation_bases = [Mutation]

    for app in get_app_packages():
        schema_mod = get_app_module(app, "schema")
        if not schema_mod:
            # The app does not define a schema
            continue

        if AppQuery := getattr(schema_mod, "Query", None):
            query_bases.append(AppQuery)
        if AppMutation := getattr(schema_mod, "Mutation", None):
            mutation_bases.append(AppMutation)

    # Define classes using all query/mutation classes as mixins
    #  cf. https://docs.graphene-python.org/projects/django/en/latest/schema/#adding-to-the-schema
    GlobalQuery = type("GlobalQuery", tuple(query_bases), {})
    GlobalMutation = type("GlobalMutation", tuple(mutation_bases), {})

    return graphene.Schema(query=GlobalQuery, mutation=GlobalMutation)


schema = build_global_schema()
