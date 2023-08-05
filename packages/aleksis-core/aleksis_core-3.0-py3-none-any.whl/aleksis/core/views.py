from textwrap import wrap
from typing import Any, Dict, Optional, Type
from urllib.parse import urlencode, urlparse, urlunparse

from django.apps import apps
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.forms.models import BaseModelForm, modelform_factory
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
    JsonResponse,
    QueryDict,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.templatetags.static import static
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.defaults import ERROR_500_TEMPLATE_NAME
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import DeleteView, FormView
from django.views.generic.list import ListView

import reversion
from allauth.account.utils import has_verified_email, send_email_confirmation
from allauth.account.views import PasswordChangeView, PasswordResetView, SignupView
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialAccount
from django_celery_results.models import TaskResult
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableMixin, SingleTableView
from dynamic_preferences.forms import preference_form_builder
from graphene_django.views import GraphQLView
from graphql import GraphQLError
from guardian.shortcuts import GroupObjectPermission, UserObjectPermission, get_objects_for_user
from haystack.generic_views import SearchView
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from haystack.utils.loading import UnifiedIndex
from health_check.views import MainView
from invitations.views import SendInvite
from maintenance_mode.core import set_maintenance_mode
from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.models import get_application_model
from oauth2_provider.views import AuthorizationView
from reversion import set_user
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin, permission_required
from two_factor import views as two_factor_views
from two_factor.utils import devices_for_user
from two_factor.views.core import LoginView as AllAuthLoginView

from aleksis.core.data_checks import DataCheck, check_data

from .celery import app
from .decorators import pwa_cache
from .filters import (
    GroupFilter,
    GroupGlobalPermissionFilter,
    GroupObjectPermissionFilter,
    PersonFilter,
    UserGlobalPermissionFilter,
    UserObjectPermissionFilter,
)
from .forms import (
    AccountRegisterForm,
    AnnouncementForm,
    AssignPermissionForm,
    ChildGroupsForm,
    DashboardWidgetOrderFormSet,
    EditAdditionalFieldForm,
    EditGroupForm,
    EditGroupTypeForm,
    GroupPreferenceForm,
    InvitationCodeForm,
    MaintenanceModeForm,
    OAuthApplicationForm,
    PersonForm,
    PersonPreferenceForm,
    SchoolTermForm,
    SelectPermissionForm,
    SitePreferenceForm,
)
from .mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView, SuccessNextMixin
from .models import (
    AdditionalField,
    Announcement,
    DashboardWidget,
    DashboardWidgetOrder,
    DataCheckResult,
    Group,
    GroupType,
    OAuthApplication,
    Person,
    PersonInvitation,
    SchoolTerm,
)
from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .tables import (
    AdditionalFieldsTable,
    DashboardWidgetTable,
    FullPersonsTable,
    GroupGlobalPermissionTable,
    GroupObjectPermissionTable,
    GroupsTable,
    GroupTypesTable,
    InvitationsTable,
    PersonsTable,
    SchoolTermTable,
    UserGlobalPermissionTable,
    UserObjectPermissionTable,
)
from .util import messages
from .util.celery_progress import render_progress_page
from .util.core_helpers import (
    generate_random_code,
    get_allowed_object_ids,
    get_pwa_icons,
    get_site_preferences,
    has_person,
    objectgetter_optional,
)
from .util.forms import PreferenceLayout
from .util.pdf import render_pdf


class LogoView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        image = request.site.preferences["theme__logo"]
        if image:
            image = image.url
        else:
            image = static("img/aleksis-banner.svg")
        return redirect(image)


class RenderPDFView(TemplateView):
    """View to render a PDF file from a template.

    Makes use of ``render_pdf``.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        return render_pdf(request, self.template_name, context)


class ServiceWorkerView(View):
    """Render serviceworker.js under root URL.

    This can't be done by static files,
    because the PWA has a scope and
    only accepts service worker files from the root URL.
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return HttpResponse(
            open(settings.SERVICE_WORKER_PATH, "rt"), content_type="application/javascript"
        )


class ManifestView(View):
    """Build manifest.json for PWA."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        prefs = get_site_preferences()
        pwa_imgs = get_pwa_icons()

        icons = [
            {
                "src": favicon_img.faviconImage.url,
                "sizes": f"{favicon_img.size}x{favicon_img.size}",
                "purpose": "maskable any" if prefs["theme__pwa_icon_maskable"] else "any",
            }
            for favicon_img in pwa_imgs
        ]

        manifest = {
            "name": prefs["general__title"],
            "short_name": prefs["general__title"],
            "description": prefs["general__description"],
            "start_url": "/",
            "scope": "/",
            "lang": get_language(),
            "display": "standalone",
            "orientation": "any",
            "status_bar": "default",
            "background_color": "#ffffff",
            "theme_color": prefs["theme__primary"],
            "icons": icons,
        }
        return JsonResponse(manifest)


@method_decorator(pwa_cache, name="dispatch")
class OfflineView(TemplateView):
    """Show an error page if there is no internet connection."""

    template_name = "offline.html"


@pwa_cache
@permission_required("core.view_dashboard_rule")
def index(request: HttpRequest) -> HttpResponse:
    """View for dashboard."""
    context = {}

    if has_person(request.user):
        person = request.user.person
        widgets = person.dashboard_widgets
        activities = person.activities.all().order_by("-created")[:5]
        notifications = person.notifications.filter(send_at__lte=timezone.now()).order_by(
            "-created"
        )[:5]
        unread_notifications = person.notifications.filter(
            send_at__lte=timezone.now(), read=False
        ).order_by("-created")
        announcements = Announcement.objects.at_time().for_person(person)
        activities = person.activities.all().order_by("-created")[:5]

    else:
        person = None
        activities = []
        notifications = []
        unread_notifications = []
        widgets = []
        announcements = []

    if len(widgets) == 0:
        # Use default dashboard if there are no widgets
        widgets = DashboardWidgetOrder.default_dashboard_widgets
        context["default_dashboard"] = True

    media = DashboardWidget.get_media(widgets)
    show_edit_dashboard_button = not getattr(person, "is_dummy", False)

    context["widgets"] = widgets
    context["media"] = media
    context["show_edit_dashboard_button"] = show_edit_dashboard_button
    context["activities"] = activities
    context["announcements"] = announcements

    return render(request, "core/index.html", context)


@method_decorator(pwa_cache, name="dispatch")
class SchoolTermListView(PermissionRequiredMixin, SingleTableView):
    """Table of all school terms."""

    model = SchoolTerm
    table_class = SchoolTermTable
    permission_required = "core.view_schoolterm_rule"
    template_name = "core/school_term/list.html"


@method_decorator(never_cache, name="dispatch")
class SchoolTermCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for school terms."""

    model = SchoolTerm
    form_class = SchoolTermForm
    permission_required = "core.add_schoolterm_rule"
    template_name = "core/school_term/create.html"
    success_url = reverse_lazy("school_terms")
    success_message = _("The school term has been created.")


@method_decorator(never_cache, name="dispatch")
class SchoolTermEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for school terms."""

    model = SchoolTerm
    form_class = SchoolTermForm
    permission_required = "core.edit_schoolterm"
    template_name = "core/school_term/edit.html"
    success_url = reverse_lazy("school_terms")
    success_message = _("The school term has been saved.")


@pwa_cache
@permission_required("core.view_persons_rule")
def persons(request: HttpRequest) -> HttpResponse:
    """List view listing all persons."""
    context = {}

    # Get all persons
    persons = get_objects_for_user(request.user, "core.view_person", Person.objects.all())

    # Get filter
    persons_filter = PersonFilter(request.GET, queryset=persons)
    context["persons_filter"] = persons_filter

    # Build table
    persons_table = PersonsTable(persons_filter.qs)
    RequestConfig(request).configure(persons_table)
    context["persons_table"] = persons_table

    return render(request, "core/person/list.html", context)


@pwa_cache
@permission_required("core.view_group_rule", fn=objectgetter_optional(Group, None, False))
def group(request: HttpRequest, id_: int) -> HttpResponse:
    """Detail view for one group."""
    context = {}

    group = objectgetter_optional(Group, None, False)(request, id_)
    context["group"] = group

    # Get group
    group = Group.objects.get(pk=id_)

    # Get members
    members = group.members.all()

    # Build table
    members_table = FullPersonsTable(members)
    RequestConfig(request).configure(members_table)
    context["members_table"] = members_table

    # Get owners
    owners = group.owners.all()

    # Build table
    owners_table = FullPersonsTable(owners)
    RequestConfig(request).configure(owners_table)
    context["owners_table"] = owners_table

    # Get statistics
    context["stats"] = group.get_group_stats

    return render(request, "core/group/full.html", context)


@pwa_cache
@permission_required("core.view_groups_rule")
def groups(request: HttpRequest) -> HttpResponse:
    """List view for listing all groups."""
    context = {}

    # Get all groups
    groups = get_objects_for_user(request.user, "core.view_group", Group)

    # Get filter
    groups_filter = GroupFilter(request.GET, queryset=groups)
    context["groups_filter"] = groups_filter

    # Build table
    groups_table = GroupsTable(groups_filter.qs)
    RequestConfig(request).configure(groups_table)
    context["groups_table"] = groups_table

    return render(request, "core/group/list.html", context)


@never_cache
@permission_required("core.assign_child_groups_to_groups_rule")
def groups_child_groups(request: HttpRequest) -> HttpResponse:
    """View for batch-processing assignment from child groups to groups."""
    context = {}

    # Apply filter
    filter_ = GroupFilter(request.GET, queryset=Group.objects.all())
    context["filter"] = filter_

    # Paginate
    paginator = Paginator(filter_.qs, 1)
    page_number = request.POST.get("page", request.POST.get("old_page"))

    if page_number:
        page = paginator.get_page(page_number)
        group = page[0]

        if "save" in request.POST:
            form = ChildGroupsForm(request.POST)
            form.is_valid()

            if "child_groups" in form.cleaned_data:
                group.child_groups.set(form.cleaned_data["child_groups"])
                group.save()
                messages.success(request, _("The child groups were successfully saved."))
        else:
            # Init form
            form = ChildGroupsForm(initial={"child_groups": group.child_groups.all()})

        context["paginator"] = paginator
        context["page"] = page
        context["group"] = group
        context["form"] = form

    return render(request, "core/group/child_groups.html", context)


@method_decorator(never_cache, name="dispatch")
class CreatePersonView(PermissionRequiredMixin, AdvancedCreateView):
    form_class = PersonForm
    model = Person
    permission_required = "core.create_person_rule"
    template_name = "core/person/create.html"
    success_message = _("The person has been saved.")


@method_decorator(never_cache, name="dispatch")
class EditPersonView(PermissionRequiredMixin, RevisionMixin, AdvancedEditView):
    form_class = PersonForm
    model = Person
    permission_required = "core.edit_person_rule"
    context_object_name = "person"
    template_name = "core/person/edit.html"
    success_message = _("The person has been saved.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        if self.object == self.request.user.person:
            # Get all changed fields and send a notification about them
            notification_fields = get_site_preferences()["account__notification_on_person_change"]
            send_notification_fields = set(form.changed_data).intersection(set(notification_fields))

            if send_notification_fields:
                self.object.notify_about_changed_data(send_notification_fields)
        return super().form_valid(form)


def get_group_by_id(request: HttpRequest, id_: Optional[int] = None):
    if id_:
        return get_object_or_404(Group, id=id_)
    else:
        return None


@never_cache
@permission_required("core.edit_group_rule", fn=objectgetter_optional(Group, None, False))
def edit_group(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a group."""
    context = {}

    group = objectgetter_optional(Group, None, False)(request, id_)
    context["group"] = group

    if id_:
        # Edit form for existing group
        edit_group_form = EditGroupForm(request.POST or None, instance=group)
    else:
        # Empty form to create a new group
        if request.user.has_perm("core.create_group_rule"):
            edit_group_form = EditGroupForm(request.POST or None)
        else:
            raise PermissionDenied()

    if request.method == "POST":
        if edit_group_form.is_valid():
            with reversion.create_revision():
                set_user(request.user)
                group = edit_group_form.save(commit=True)

            messages.success(request, _("The group has been saved."))

            return redirect("group_by_id", group.pk)

    context["edit_group_form"] = edit_group_form

    return render(request, "core/group/edit.html", context)


@method_decorator(pwa_cache, name="dispatch")
class SystemStatus(PermissionRequiredMixin, MainView):
    """View giving information about the system status."""

    template_name = "core/pages/system_status.html"
    permission_required = "core.view_system_status_rule"
    context = {}

    def get(self, request, *args, **kwargs):
        task_results = []

        if app.control.inspect().registered_tasks():
            job_list = list(app.control.inspect().registered_tasks().values())[0]
            for job in job_list:
                task_results.append(
                    TaskResult.objects.filter(task_name=job).order_by("date_done").last()
                )

        context = {
            "plugins": self.plugins,
            "tasks": task_results,
            "DEBUG": settings.DEBUG,
            "form": MaintenanceModeForm(),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = MaintenanceModeForm(request.POST)

        if form.is_valid():
            mode = form.cleaned_data.get("maintenance_mode")
        else:
            return HttpResponseBadRequest()

        if not request.user.is_superuser:
            return self.handle_no_permission()

        set_maintenance_mode(mode)
        if mode:
            messages.success(request, _("Maintenance mode was turned on successfully."))
        else:
            messages.success(request, _("Maintenance mode was turned off successfully."))

        return self.get(request, *args, **kwargs)


class SystemStatusAPIView(PermissionRequiredMixin, MainView):
    """Provide information about system status as JSON."""

    permission_required = "core.view_system_status_rule"

    @method_decorator(never_cache)
    def get(self, request, *args, **kwargs):
        status_code = 500 if self.errors else 200

        return self.render_to_response_json(self.plugins, status_code)


class TestPDFGenerationView(PermissionRequiredMixin, RenderPDFView):
    template_name = "core/pages/test_pdf.html"
    permission_required = "core.test_pdf_rule"


@pwa_cache
@permission_required("core.view_announcements_rule")
def announcements(request: HttpRequest) -> HttpResponse:
    """List view of announcements."""
    context = {}

    # Get all announcements
    announcements = Announcement.objects.all()
    context["announcements"] = announcements

    return render(request, "core/announcement/list.html", context)


@never_cache
@permission_required(
    "core.create_or_edit_announcement_rule", fn=objectgetter_optional(Announcement, None, False)
)
def announcement_form(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to create or edit an announcement."""
    context = {}

    announcement = objectgetter_optional(Announcement, None, False)(request, id_)

    if announcement:
        # Edit form for existing announcement
        form = AnnouncementForm(request.POST or None, instance=announcement)
        context["mode"] = "edit"
    else:
        # Empty form to create new announcement
        form = AnnouncementForm(request.POST or None)
        context["mode"] = "add"

    if request.method == "POST":
        if form.is_valid():
            form.save()

            messages.success(request, _("The announcement has been saved."))
            return redirect("announcements")

    context["form"] = form

    return render(request, "core/announcement/form.html", context)


@permission_required(
    "core.delete_announcement_rule", fn=objectgetter_optional(Announcement, None, False)
)
def delete_announcement(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an announcement."""
    if request.method == "POST":
        announcement = objectgetter_optional(Announcement, None, False)(request, id_)
        announcement.delete()
        messages.success(request, _("The announcement has been deleted."))

    return redirect("announcements")


@permission_required("core.search_rule")
def searchbar_snippets(request: HttpRequest) -> HttpResponse:
    """View to return HTML snippet with searchbar autocompletion results."""
    query = request.GET.get("q", "")
    limit = int(request.GET.get("limit", "5"))
    indexed_models = UnifiedIndex().get_indexed_models()
    allowed_object_ids = get_allowed_object_ids(request, indexed_models)
    results = (
        SearchQuerySet().filter(id__in=allowed_object_ids).filter(text=AutoQuery(query))[:limit]
    )
    context = {"results": results}

    return render(request, "search/searchbar_snippets.html", context)


@method_decorator(pwa_cache, name="dispatch")
class PermissionSearchView(PermissionRequiredMixin, SearchView):
    """Wrapper to apply permission to haystack's search view."""

    permission_required = "core.search_rule"

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        indexed_models = UnifiedIndex().get_indexed_models()
        allowed_object_ids = get_allowed_object_ids(self.request, indexed_models)
        queryset = queryset.filter(id__in=allowed_object_ids)

        return super().get_context_data(object_list=queryset, **kwargs)


@never_cache
def preferences(
    request: HttpRequest,
    registry_name: str = "person",
    pk: Optional[int] = None,
    section: Optional[str] = None,
) -> HttpResponse:
    """View for changing preferences."""
    context = {}

    # Decide which registry to use and check preferences
    if registry_name == "site":
        registry = site_preferences_registry
        instance = request.site
        form_class = SitePreferenceForm

        if not request.user.has_perm("core.change_site_preferences_rule", instance):
            raise PermissionDenied()
    elif registry_name == "person":
        registry = person_preferences_registry
        instance = objectgetter_optional(Person, "request.user.person", True)(request, pk)
        form_class = PersonPreferenceForm

        if not request.user.has_perm("core.change_person_preferences_rule", instance):
            raise PermissionDenied()
    elif registry_name == "group":
        registry = group_preferences_registry
        instance = objectgetter_optional(Group, None, False)(request, pk)
        form_class = GroupPreferenceForm

        if not request.user.has_perm("core.change_group_preferences_rule", instance):
            raise PermissionDenied()
    else:
        # Invalid registry name passed from URL
        raise Http404(_("The requested preference registry does not exist"))

    if not section and len(registry.sections()) > 0:
        default_section = list(registry.sections())[0]
        if instance:
            return redirect(f"preferences_{registry_name}", instance.pk, default_section)
        else:
            return redirect(f"preferences_{registry_name}", default_section)

    # Build final form from dynamic-preferences
    form_class = preference_form_builder(form_class, instance=instance, section=section)

    # Get layout
    form_class.layout = PreferenceLayout(form_class, section=section)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES or None)
        if form.is_valid():
            form.update_preferences()
            messages.success(request, _("The preferences have been saved successfully."))
    else:
        form = form_class()

    context["registry"] = registry
    context["registry_name"] = registry_name
    context["section"] = section
    context["registry_url"] = "preferences_" + registry_name
    context["form"] = form
    context["instance"] = instance

    return render(request, "dynamic_preferences/form.html", context)


@permission_required("core.delete_person_rule", fn=objectgetter_optional(Person))
def delete_person(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an person."""
    person = objectgetter_optional(Person)(request, id_)

    with reversion.create_revision():
        set_user(request.user)
        person.save()

    person.delete()
    messages.success(request, _("The person has been deleted."))

    return redirect("persons")


@permission_required("core.delete_group_rule", fn=objectgetter_optional(Group))
def delete_group(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an group."""
    group = objectgetter_optional(Group)(request, id_)
    with reversion.create_revision():
        set_user(request.user)
        group.save()

    group.delete()
    messages.success(request, _("The group has been deleted."))

    return redirect("groups")


@never_cache
@permission_required(
    "core.change_additionalfield_rule", fn=objectgetter_optional(AdditionalField, None, False)
)
def edit_additional_field(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a additional_field."""
    context = {}

    additional_field = objectgetter_optional(AdditionalField, None, False)(request, id_)
    context["additional_field"] = additional_field

    if id_:
        # Edit form for existing additional_field
        edit_additional_field_form = EditAdditionalFieldForm(
            request.POST or None, instance=additional_field
        )
    else:
        if request.user.has_perm("core.create_additionalfield_rule"):
            # Empty form to create a new additional_field
            edit_additional_field_form = EditAdditionalFieldForm(request.POST or None)
        else:
            raise PermissionDenied()

    if request.method == "POST":
        if edit_additional_field_form.is_valid():
            edit_additional_field_form.save(commit=True)

            messages.success(request, _("The additional field has been saved."))

            return redirect("additional_fields")

    context["edit_additional_field_form"] = edit_additional_field_form

    return render(request, "core/additional_field/edit.html", context)


@pwa_cache
@permission_required("core.view_additionalfields_rule")
def additional_fields(request: HttpRequest) -> HttpResponse:
    """List view for listing all additional fields."""
    context = {}

    # Get all additional fields
    additional_fields = get_objects_for_user(
        request.user, "core.view_additionalfield", AdditionalField
    )

    # Build table
    additional_fields_table = AdditionalFieldsTable(additional_fields)
    RequestConfig(request).configure(additional_fields_table)
    context["additional_fields_table"] = additional_fields_table

    return render(request, "core/additional_field/list.html", context)


@permission_required(
    "core.delete_additionalfield_rule", fn=objectgetter_optional(AdditionalField, None, False)
)
def delete_additional_field(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an additional field."""
    additional_field = objectgetter_optional(AdditionalField, None, False)(request, id_)
    additional_field.delete()
    messages.success(request, _("The additional field has been deleted."))

    return redirect("additional_fields")


@never_cache
@permission_required("core.change_grouptype_rule", fn=objectgetter_optional(GroupType, None, False))
def edit_group_type(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a group_type."""
    context = {}

    group_type = objectgetter_optional(GroupType, None, False)(request, id_)
    context["group_type"] = group_type

    if id_:
        # Edit form for existing group_type
        edit_group_type_form = EditGroupTypeForm(request.POST or None, instance=group_type)
    else:
        # Empty form to create a new group_type
        edit_group_type_form = EditGroupTypeForm(request.POST or None)

    if request.method == "POST":
        if edit_group_type_form.is_valid():
            edit_group_type_form.save(commit=True)

            messages.success(request, _("The group type has been saved."))

            return redirect("group_types")

    context["edit_group_type_form"] = edit_group_type_form

    return render(request, "core/group_type/edit.html", context)


@pwa_cache
@permission_required("core.view_grouptypes_rule")
def group_types(request: HttpRequest) -> HttpResponse:
    """List view for listing all group types."""
    context = {}

    # Get all group types
    group_types = get_objects_for_user(request.user, "core.view_grouptype", GroupType)

    # Build table
    group_types_table = GroupTypesTable(group_types)
    RequestConfig(request).configure(group_types_table)
    context["group_types_table"] = group_types_table

    return render(request, "core/group_type/list.html", context)


@permission_required("core.delete_grouptype_rule", fn=objectgetter_optional(GroupType, None, False))
def delete_group_type(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an group_type."""
    group_type = objectgetter_optional(GroupType, None, False)(request, id_)
    group_type.delete()
    messages.success(request, _("The group type has been deleted."))

    return redirect("group_types")


@method_decorator(pwa_cache, name="dispatch")
class DataCheckView(PermissionRequiredMixin, ListView):
    permission_required = "core.view_datacheckresults_rule"
    model = DataCheckResult
    template_name = "core/data_check/list.html"
    context_object_name = "results"

    def get_queryset(self) -> QuerySet:
        return (
            DataCheckResult.objects.filter(content_type__app_label__in=apps.app_configs.keys())
            .filter(solved=False)
            .order_by("data_check")
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["registered_checks"] = DataCheck.registered_objects_list
        return context


@method_decorator(pwa_cache, name="dispatch")
class RunDataChecks(PermissionRequiredMixin, View):
    permission_required = "core.run_data_checks_rule"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        result = check_data.delay()

        return render_progress_page(
            request,
            result,
            title=_("Progress: Run data checks"),
            progress_title=_("Run data checks …"),
            success_message=_("The data checks were run successfully."),
            error_message=_("There was a problem while running data checks."),
            back_url="/data_checks/",
        )


@method_decorator(pwa_cache, name="dispatch")
class SolveDataCheckView(PermissionRequiredMixin, RevisionMixin, DetailView):
    queryset = DataCheckResult.objects.all()
    permission_required = "core.solve_data_problem_rule"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        solve_option = self.kwargs["solve_option"]
        result = self.get_object()
        if solve_option in result.related_check.solve_options:
            solve_option_obj = result.related_check.solve_options[solve_option]

            msg = _(
                f"The solve option '{solve_option_obj.verbose_name}' "
                f"has been executed on the object '{result.related_object}' "
                f"(type: {result.related_object._meta.verbose_name})."
            )

            result.solve(solve_option)

            messages.success(request, msg)
            return redirect("check_data")
        else:
            raise Http404(_("The requested solve option does not exist"))


@method_decorator(pwa_cache, name="dispatch")
class DashboardWidgetListView(PermissionRequiredMixin, SingleTableView):
    """Table of all dashboard widgets."""

    model = DashboardWidget
    table_class = DashboardWidgetTable
    permission_required = "core.view_dashboardwidget_rule"
    template_name = "core/dashboard_widget/list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["widget_types"] = [
            (ContentType.objects.get_for_model(m, False), m)
            for m in DashboardWidget.registered_objects_list
        ]
        return context


@method_decorator(never_cache, name="dispatch")
class DashboardWidgetEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for dashboard widgets."""

    def get_form_class(self) -> Type[BaseModelForm]:
        return modelform_factory(self.object.__class__, fields=self.fields)

    model = DashboardWidget
    fields = "__all__"
    permission_required = "core.edit_dashboardwidget_rule"
    template_name = "core/dashboard_widget/edit.html"
    success_url = reverse_lazy("dashboard_widgets")
    success_message = _("The dashboard widget has been saved.")


@method_decorator(never_cache, name="dispatch")
class DashboardWidgetCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for dashboard widgets."""

    def get_model(self, request, *args, **kwargs):
        app_label = kwargs.get("app")
        model = kwargs.get("model")
        ct = get_object_or_404(ContentType, app_label=app_label, model=model)
        return ct.model_class()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        return context

    def get(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    fields = "__all__"
    permission_required = "core.add_dashboardwidget_rule"
    template_name = "core/dashboard_widget/create.html"
    success_url = reverse_lazy("dashboard_widgets")
    success_message = _("The dashboard widget has been created.")


class DashboardWidgetDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete view for dashboard widgets."""

    model = DashboardWidget
    permission_required = "core.delete_dashboardwidget_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("dashboard_widgets")
    success_message = _("The dashboard widget has been deleted.")


class EditDashboardView(PermissionRequiredMixin, View):
    """View for editing dashboard widget order."""

    permission_required = "core.edit_dashboard_rule"

    def get_context_data(self, request, **kwargs):
        context = {}
        self.default_dashboard = kwargs.get("default", False)

        if (
            self.default_dashboard
            and not request.user.has_perm("core.edit_default_dashboard_rule")
            or getattr(request.user, "person", True)
            and getattr(request.user.person, "is_dummy", False)
        ):
            raise PermissionDenied()

        context["default_dashboard"] = self.default_dashboard

        widgets = (
            request.user.person.dashboard_widgets
            if not self.default_dashboard
            else DashboardWidgetOrder.default_dashboard_widgets
        )
        not_used_widgets = DashboardWidget.objects.exclude(pk__in=[w.pk for w in widgets]).filter(
            active=True
        )
        context["widgets"] = widgets
        context["not_used_widgets"] = not_used_widgets

        order = 10
        initial = []
        for widget in widgets:
            initial.append({"pk": widget, "order": order})
            order += 10
        for widget in not_used_widgets:
            initial.append({"pk": widget, "order": 0})

        formset = DashboardWidgetOrderFormSet(
            request.POST or None, initial=initial, prefix="widget_order"
        )
        context["formset"] = formset

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)

        if context["formset"].is_valid():
            added_objects = []
            for form in context["formset"]:
                if not form.cleaned_data["order"]:
                    continue

                obj, created = DashboardWidgetOrder.objects.update_or_create(
                    widget=form.cleaned_data["pk"],
                    person=request.user.person if not self.default_dashboard else None,
                    default=self.default_dashboard,
                    defaults={"order": form.cleaned_data["order"]},
                )

                added_objects.append(obj.pk)

            DashboardWidgetOrder.objects.filter(
                person=request.user.person if not self.default_dashboard else None,
                default=self.default_dashboard,
            ).exclude(pk__in=added_objects).delete()

            if not self.default_dashboard:
                msg = _("Your dashboard configuration has been saved successfully.")
            else:
                msg = _("The configuration of the default dashboard has been saved successfully.")
            messages.success(request, msg)
            return redirect("index" if not self.default_dashboard else "dashboard_widgets")

    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)

        return render(request, "core/edit_dashboard.html", context=context)


class InvitePerson(PermissionRequiredMixin, SingleTableView, SendInvite):
    """View to invite a person to register an account."""

    template_name = "invitations/forms/_invite.html"
    permission_required = "core.invite_rule"
    model = PersonInvitation
    table_class = InvitationsTable
    context = {}

    def dispatch(self, request, *args, **kwargs):
        if not get_site_preferences()["auth__invite_enabled"]:
            return HttpResponseRedirect(reverse_lazy("invite_disabled"))
        return super().dispatch(request, *args, **kwargs)

    # Get queryset of invitations
    def get_context_data(self, **kwargs):
        queryset = kwargs.pop("object_list", None)
        if queryset is None:
            self.object_list = self.model.objects.all()
        return super().get_context_data(**kwargs)


class EnterInvitationCode(FormView):
    """View to enter an invitation code."""

    template_name = "invitations/enter.html"
    form_class = InvitationCodeForm

    def form_valid(self, form):
        code = "".join(form.cleaned_data["code"].lower().split("-"))
        # Check if valid invitations exists
        if (
            PersonInvitation.objects.filter(key=code).exists()
            and not PersonInvitation.objects.get(key=code).accepted
            and not PersonInvitation.objects.get(key=code).key_expired()
        ):
            self.request.session["invitation_code"] = code
            return redirect("account_signup")
        return redirect("invitations:accept-invite", code)


class GenerateInvitationCode(View):
    """View to generate an invitation code."""

    def get(self, request):
        # Build code
        length = get_site_preferences()["auth__invite_code_length"]
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        code = generate_random_code(length, packet_size)

        # Create invitation object
        invitation = PersonInvitation.objects.create(
            email="", inviter=request.user, key=code, sent=timezone.now()
        )

        # Make code more readable
        code = "-".join(wrap(invitation.key, 5))

        # Generate success message and print code
        messages.success(
            request,
            _(f"The invitation was successfully created. The invitation code is {code}"),
        )

        return redirect("invite_person")


@method_decorator(pwa_cache, name="dispatch")
class PermissionsListBaseView(PermissionRequiredMixin, SingleTableMixin, FilterView):
    """Base view for list of all permissions."""

    template_name = "core/perms/list.html"
    permission_required = "core.manage_permissions_rule"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assign_form"] = SelectPermissionForm()
        context["tab"] = self.tab

        return context


@method_decorator(pwa_cache, name="dispatch")
class UserGlobalPermissionsListBaseView(PermissionsListBaseView):
    """List all global user permissions."""

    filterset_class = UserGlobalPermissionFilter
    table_class = UserGlobalPermissionTable
    tab = "user_global"


@method_decorator(pwa_cache, name="dispatch")
class GroupGlobalPermissionsListBaseView(PermissionsListBaseView):
    """List all global group permissions."""

    filterset_class = GroupGlobalPermissionFilter
    table_class = GroupGlobalPermissionTable
    tab = "group_global"


@method_decorator(pwa_cache, name="dispatch")
class UserObjectPermissionsListBaseView(PermissionsListBaseView):
    """List all object user permissions."""

    filterset_class = UserObjectPermissionFilter
    table_class = UserObjectPermissionTable
    tab = "user_object"


@method_decorator(pwa_cache, name="dispatch")
class GroupObjectPermissionsListBaseView(PermissionsListBaseView):
    """List all object group permissions."""

    filterset_class = GroupObjectPermissionFilter
    table_class = GroupObjectPermissionTable
    tab = "group_object"


@method_decorator(pwa_cache, name="dispatch")
class SelectPermissionForAssignView(PermissionRequiredMixin, FormView):
    """View for selecting a permission to assign."""

    permission_required = "core.manage_permissions_rule"
    form_class = SelectPermissionForm

    def form_valid(self, form: SelectPermissionForm) -> HttpResponse:
        url = reverse("assign_permission", args=[form.cleaned_data["selected_permission"].pk])
        params = {"next": self.request.GET["next"]} if "next" in self.request.GET else {}
        return redirect(f"{url}?{urlencode(params)}")

    def form_invalid(self, form: SelectPermissionForm) -> HttpResponse:
        return redirect("manage_group_object_permissions")


class AssignPermissionView(SuccessNextMixin, PermissionRequiredMixin, DetailView, FormView):
    """View for assigning a permission to users/groups for all/some objects."""

    permission_required = "core.manage_permissions"
    queryset = Permission.objects.all()
    template_name = "core/perms/assign.html"
    form_class = AssignPermissionForm
    success_url = "manage_user_global_permissions"

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["permission"] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # Overwrite get_context_data to ensure correct function call order
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form: AssignPermissionForm) -> HttpResponse:
        form.save_perms()
        messages.success(
            self.request,
            _("We have successfully assigned the permissions."),
        )
        return redirect(self.get_success_url())


class UserGlobalPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a global user permission."""

    permission_required = "core.manage_permissions"
    model = User.user_permissions.through
    success_message = _("The global user permission has been deleted.")
    success_url = reverse_lazy("manage_user_global_permissions")
    template_name = "core/pages/delete.html"


class GroupGlobalPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a global group permission."""

    permission_required = "core.manage_permissions"
    model = DjangoGroup.permissions.through
    success_message = _("The global group permission has been deleted.")
    success_url = reverse_lazy("manage_group_global_permissions")
    template_name = "core/pages/delete.html"


class UserObjectPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a object user permission."""

    permission_required = "core.manage_permissions"
    model = UserObjectPermission
    success_message = _("The object user permission has been deleted.")
    success_url = reverse_lazy("manage_user_object_permissions")
    template_name = "core/pages/delete.html"


class GroupObjectPermissionDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete a object group permission."""

    permission_required = "core.manage_permissions"
    model = GroupObjectPermission
    success_message = _("The object group permission has been deleted.")
    success_url = reverse_lazy("manage_group_object_permissions")
    template_name = "core/pages/delete.html"


@method_decorator(pwa_cache, name="dispatch")
class OAuth2ListView(PermissionRequiredMixin, ListView):
    """List view for all the applications."""

    permission_required = "core.view_oauthapplications_rule"
    context_object_name = "applications"
    template_name = "oauth2_provider/application/list.html"

    def get_queryset(self):
        return OAuthApplication.objects.all()


@method_decorator(pwa_cache, name="dispatch")
class OAuth2DetailView(PermissionRequiredMixin, DetailView):
    """Detail view for an application instance."""

    context_object_name = "application"
    permission_required = "core.view_oauthapplication_rule"
    template_name = "oauth2_provider/application/detail.html"

    def get_queryset(self):
        return OAuthApplication.objects.all()


class OAuth2DeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """View used to delete an application."""

    permission_required = "core.delete_oauthapplication_rule"
    context_object_name = "application"
    success_url = reverse_lazy("oauth2_applications")
    template_name = "core/pages/delete.html"

    def get_queryset(self):
        return OAuthApplication.objects.all()


class OAuth2EditView(PermissionRequiredMixin, AdvancedEditView):
    """View used to edit an application."""

    permission_required = "core.edit_oauthapplication_rule"
    context_object_name = "application"
    template_name = "oauth2_provider/application/edit.html"
    form_class = OAuthApplicationForm

    def get_queryset(self):
        return OAuthApplication.objects.all()


class OAuth2RegisterView(PermissionRequiredMixin, AdvancedCreateView):
    """View used to register an application."""

    permission_required = "core.create_oauthapplication_rule"
    context_object_name = "application"
    template_name = "oauth2_provider/application/create.html"
    form_class = OAuthApplicationForm


class CustomPasswordChangeView(LoginRequiredMixin, PermissionRequiredMixin, PasswordChangeView):
    """Custom password change view to allow to disable changing of password."""

    permission_required = "core.change_password_rule"

    def __init__(self, *args, **kwargs):
        if get_site_preferences()["auth__allow_password_change"]:
            self.template_name = "account/password_change.html"
        else:
            self.template_name = "account/password_change_disabled.html"

        super().__init__(*args, **kwargs)


class CustomPasswordResetView(PermissionRequiredMixin, PasswordResetView):
    """Custom password reset view to allow to disable resetting of password."""

    permission_required = "core.reset_password_rule"

    def __init__(self, *args, **kwargs):
        if get_site_preferences()["auth__allow_password_reset"]:
            self.template_name = "account/password_reset.html"
        else:
            self.template_name = "account/password_change_disabled.html"

        super().__init__(*args, **kwargs)


class SocialAccountDeleteView(DeleteView):
    """Custom view to delete django-allauth social account."""

    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("socialaccount_connections")

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            get_adapter(self.request).validate_disconnect(
                self.object, SocialAccount.objects.filter(user=self.request.user)
            )
        except ValidationError:
            messages.error(
                self.request,
                _(
                    "The third-party account could not be disconnected "
                    "because it is the only login method available."
                ),
            )
        else:
            self.object.delete()
            messages.success(
                self.request, _("The third-party account has been successfully disconnected.")
            )
        return super().form_valid()


def server_error(
    request: HttpRequest, template_name: str = ERROR_500_TEMPLATE_NAME
) -> HttpResponseServerError:
    """Ensure the request is passed to the error page."""
    template = loader.get_template(template_name)
    context = {"request": request}

    return HttpResponseServerError(template.render(context))


class AccountRegisterView(SignupView):
    """Custom view to register a user account.

    Rewrites dispatch function from allauth to check if signup is open or if the user
    has a verified email address from an invitation; otherwise raises permission denied.
    """

    form_class = AccountRegisterForm
    success_url = reverse_lazy("index")

    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.has_perm("core.signup_rule")
            and not request.session.get("account_verified_email")
            and not request.session.get("invitation_code")
        ):
            raise PermissionDenied()
        return super(AccountRegisterView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AccountRegisterView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["login_url"] = reverse(settings.LOGIN_URL)
        return context


class InvitePersonByID(PermissionRequiredMixin, SingleObjectMixin, View):
    """Custom view to invite person by their ID."""

    model = Person
    success_url = reverse_lazy("persons")
    permission_required = "core.invite_rule"

    def dispatch(self, request, *args, **kwargs):
        if not get_site_preferences()["auth__invite_enabled"]:
            return HttpResponseRedirect(reverse_lazy("invite_disabled"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        person = self.get_object()

        if not person.email or not PersonInvitation.objects.filter(email=person.email).exists():
            length = get_site_preferences()["auth__invite_code_length"]
            packet_size = get_site_preferences()["auth__invite_code_packet_size"]
            key = generate_random_code(length, packet_size)
            invite = PersonInvitation.objects.create(person=person, key=key)
            if person.email:
                invite.email = person.email
            invite.inviter = self.request.user
            invite.save()

            invite.send_invitation(self.request)

            if person.email:
                messages.success(
                    self.request,
                    _(
                        "Person was invited successfully and an email "
                        "with further instructions has been send to them."
                    ),
                )
            else:
                readable_key = "-".join(wrap(key, packet_size))
                messages.success(
                    self.request,
                    f"{_('Person was invited successfully. Their key is')} {readable_key}.",
                )
        else:
            messages.success(self.request, _("Person was already invited."))

        return HttpResponseRedirect(person.get_absolute_url())


class InviteDisabledView(PermissionRequiredMixin, TemplateView):
    """View to display a notice that the invite feature is disabled and how to enable it."""

    template_name = "invitations/disabled.html"
    permission_required = "core.change_site_preferences_rule"

    def dispatch(self, request, *args, **kwargs):
        if get_site_preferences()["auth__invite_enabled"]:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class LoginView(AllAuthLoginView):
    """Custom login view covering e-mail verification if mandatory.

    Overrides view from allauth to check if email verification from django-invitations is
    mandatory. If it i, checks if the user has a verified email address, if not,
    it re-sends verification.
    """

    def done(self, form_list, **kwargs):
        if settings.ACCOUNT_EMAIL_VERIFICATION == "mandatory":
            user = self.get_user()
            if not has_verified_email(user, user.email):
                send_email_confirmation(self.request, user, signup=False, email=user.email)
                return render(self.request, "account/verification_sent.html")

        return super().done(form_list, **kwargs)

    def get_context_data(self, form, **kwargs):
        """Override context data to hide side menu and include OAuth2 application if given."""
        context = super().get_context_data(form, **kwargs)
        if self.request.GET.get("oauth"):
            context["no_menu"] = True

            if self.request.GET.get("client_id"):
                application = get_application_model().objects.get(
                    client_id=self.request.GET["client_id"]
                )
                context["oauth_application"] = application
        return context


class CustomAuthorizationView(AuthorizationView):
    def handle_no_permission(self):
        """Override handle_no_permission to provide OAuth2 information to login page."""
        redirect_obj = super().handle_no_permission()

        try:
            scopes, credentials = self.validate_authorization_request(self.request)
        except OAuthToolkitError as error:
            # Application is not available at this time.
            return self.error_response(error, application=None)

        login_url_parts = list(urlparse(redirect_obj.url))
        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring["oauth"] = "yes"
        querystring["client_id"] = credentials["client_id"]
        login_url_parts[4] = querystring.urlencode(safe="/")

        return HttpResponseRedirect(urlunparse(login_url_parts))

    def get_context_data(self, **kwargs):
        """Override context data to hide side menu."""
        context = super().get_context_data(**kwargs)
        context["no_menu"] = True
        return context


class TwoFactorSetupView(two_factor_views.SetupView):
    def get(self, request, *args, **kwargs):
        return super(two_factor_views.SetupView, self).get(request, *args, **kwargs)

    def get_device(self, **kwargs):
        device = super().get_device(**kwargs)

        # Ensure that the device is named "backup" if it is a phone device
        # to ensure compatibility with django_two_factor_auth
        method = self.get_method()
        if device and method.code in ("call", "sms"):
            device.name = "backup"
        return device


class TwoFactorLoginView(two_factor_views.LoginView):
    def get_devices(self):
        user = self.get_user()

        return devices_for_user(user)

    def get_other_devices(self, main_device):
        other_devices = self.get_devices()
        other_devices = list(filter(lambda x: not isinstance(x, type(main_device)), other_devices))

        return other_devices


class LoggingGraphQLView(GraphQLView):
    """GraphQL view that raises unknown exceptions instead of blindly catching them."""

    def execute_graphql_request(self, *args, **kwargs):
        result = super().execute_graphql_request(*args, **kwargs)
        errors = result.errors or []
        for error in errors:
            if not isinstance(error.original_error, GraphQLError):
                raise error
        return result
