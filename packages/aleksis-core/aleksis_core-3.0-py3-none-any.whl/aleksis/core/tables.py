from textwrap import wrap

from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A

from .models import Person
from .util.core_helpers import get_site_preferences


class SchoolTermTable(tables.Table):
    """Table to list persons."""

    class Meta:
        attrs = {"class": "highlight"}

    name = tables.LinkColumn("edit_school_term", args=[A("id")])
    date_start = tables.Column()
    date_end = tables.Column()
    edit = tables.LinkColumn(
        "edit_school_term",
        args=[A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
        verbose_name=_("Actions"),
    )


class PersonsTable(tables.Table):
    """Table to list persons."""

    class Meta:
        model = Person
        attrs = {"class": "highlight"}
        fields = []

    first_name = tables.LinkColumn("person_by_id", args=[A("id")])
    last_name = tables.LinkColumn("person_by_id", args=[A("id")])


class FullPersonsTable(PersonsTable):
    """Table to list persons."""

    photo = tables.Column(verbose_name=_("Photo"), accessor="pk", orderable=False)
    address = tables.Column(verbose_name=_("Address"), accessor="pk", orderable=False)

    class Meta(PersonsTable.Meta):
        fields = (
            "photo",
            "short_name",
            "date_of_birth",
            "sex",
            "email",
            "user__username",
        )
        sequence = ("photo", "first_name", "last_name", "short_name", "...")

    def render_photo(self, value, record):
        return render_to_string(
            "core/partials/avatar_content.html",
            {
                "person_or_user": record,
                "class": "materialize-circle table-circle",
                "img_class": "materialize-circle",
            },
            self.request,
        )

    def render_address(self, value, record):
        return render_to_string(
            "core/partials/address.html",
            {
                "person": record,
            },
            self.request,
        )

    def before_render(self, request):
        """Hide columns if user has no permission to view them."""
        if not self.request.user.has_perm("core.view_person_rule"):
            self.columns.hide("date_of_birth")
            self.columns.hide("sex")
        if not self.request.user.has_perm("core.view_contact_details_rule"):
            self.columns.hide("email")
        if not self.request.user.has_perm("core.view_address"):
            self.columns.hide("street")
            self.columns.hide("housenumber")
            self.columns.hide("postal_code")
            self.columns.hide("place")


class GroupsTable(tables.Table):
    """Table to list groups."""

    class Meta:
        attrs = {"class": "highlight"}

    name = tables.LinkColumn("group_by_id", args=[A("id")])
    short_name = tables.LinkColumn("group_by_id", args=[A("id")])
    school_term = tables.Column()


class AdditionalFieldsTable(tables.Table):
    """Table to list group types."""

    class Meta:
        attrs = {"class": "hightlight"}

    title = tables.LinkColumn("edit_additional_field_by_id", args=[A("id")])
    delete = tables.LinkColumn(
        "delete_additional_field_by_id",
        args=[A("id")],
        verbose_name=_("Delete"),
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red"}},
    )


class GroupTypesTable(tables.Table):
    """Table to list group types."""

    class Meta:
        attrs = {"class": "highlight"}

    name = tables.LinkColumn("edit_group_type_by_id", args=[A("id")])
    description = tables.LinkColumn("edit_group_type_by_id", args=[A("id")])
    delete = tables.LinkColumn(
        "delete_group_type_by_id", args=[A("id")], verbose_name=_("Delete"), text=_("Delete")
    )


class DashboardWidgetTable(tables.Table):
    """Table to list dashboard widgets."""

    class Meta:
        attrs = {"class": "highlight"}

    widget_name = tables.Column(accessor="pk")
    title = tables.LinkColumn("edit_dashboard_widget", args=[A("id")])
    active = tables.BooleanColumn(yesno="check,cancel", attrs={"span": {"class": "material-icons"}})
    delete = tables.LinkColumn(
        "delete_dashboard_widget",
        args=[A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
        verbose_name=_("Actions"),
    )

    def render_widget_name(self, value, record):
        return record._meta.verbose_name


class InvitationCodeColumn(tables.Column):
    """Returns invitation code in a more readable format."""

    def render(self, value):
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        return "-".join(wrap(value, packet_size))


class InvitationsTable(tables.Table):
    """Table to list persons."""

    person = tables.Column()
    email = tables.EmailColumn()
    sent = tables.DateColumn()
    inviter = tables.Column()
    key = InvitationCodeColumn()
    accepted = tables.BooleanColumn(
        yesno="check,cancel", attrs={"span": {"class": "material-icons"}}
    )


class PermissionDeleteColumn(tables.LinkColumn):
    """Link column with label 'Delete'."""

    def __init__(self, url, **kwargs):
        super().__init__(
            url,
            args=[A("pk")],
            text=_("Delete"),
            attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
            verbose_name=_("Actions"),
            **kwargs
        )


class PermissionTable(tables.Table):
    """Table to list permissions."""

    class Meta:
        attrs = {"class": "responsive-table highlight"}

    permission = tables.Column()


class ObjectPermissionTable(PermissionTable):
    """Table to list object permissions."""

    content_object = tables.Column()


class GlobalPermissionTable(PermissionTable):
    """Table to list global permissions."""

    pass


class GroupObjectPermissionTable(ObjectPermissionTable):
    """Table to list assigned group object permissions."""

    group = tables.Column()
    delete = PermissionDeleteColumn("delete_group_object_permission")


class UserObjectPermissionTable(ObjectPermissionTable):
    """Table to list assigned user object permissions."""

    user = tables.Column()
    delete = PermissionDeleteColumn("delete_user_object_permission")


class GroupGlobalPermissionTable(GlobalPermissionTable):
    """Table to list assigned global user permissions."""

    group = tables.Column()
    delete = PermissionDeleteColumn("delete_group_global_permission")


class UserGlobalPermissionTable(GlobalPermissionTable):
    """Table to list assigned global group permissions."""

    user = tables.Column()
    delete = PermissionDeleteColumn("delete_user_global_permission")
