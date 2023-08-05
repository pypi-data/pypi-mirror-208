from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog

import calendarweek.django
from ckeditor_uploader import views as ckeditor_uploader_views
from health_check.urls import urlpatterns as health_urls
from maintenance_mode.decorators import force_maintenance_mode_off
from oauth2_provider.views import ConnectDiscoveryInfoView
from rules.contrib.views import permission_required
from two_factor.urls import urlpatterns as tf_urls

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="core/vue_index.html"), name="vue_app"),
    path("manifest.json", views.ManifestView.as_view(), name="manifest"),
    path("sw.js", views.ServiceWorkerView.as_view(), name="service_worker"),
    path(settings.MEDIA_URL.removeprefix("/"), include("titofisto.urls")),
    path("__icons__/", include("dj_iconify.urls")),
    path(
        "graphql/",
        csrf_exempt(views.LoggingGraphQLView.as_view(graphiql=True)),
        name="graphql",
    ),
    path("logo", force_maintenance_mode_off(views.LogoView.as_view()), name="logo"),
    path(
        ".well-known/openid-configuration/",
        ConnectDiscoveryInfoView.as_view(),
        name="oidc_configuration",
    ),
    path("oauth/applications/", views.TemplateView.as_view(template_name="core/vue_index.html")),
    path(
        "oauth/authorized_tokens/", views.TemplateView.as_view(template_name="core/vue_index.html")
    ),
    path("oauth/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("system_status/", views.SystemStatusAPIView.as_view(), name="system_status_api"),
    path(
        "django/",
        include(
            [
                path("", include("django_prometheus.urls")),
                path("account/login/", views.LoginView.as_view(), name="login"),
                path(
                    "accounts/signup/", views.AccountRegisterView.as_view(), name="account_signup"
                ),
                path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
                path(
                    "accounts/password/change/",
                    views.CustomPasswordChangeView.as_view(),
                    name="account_change_password",
                ),
                path(
                    "accounts/password/reset/",
                    views.CustomPasswordResetView.as_view(),
                    name="account_reset_password",
                ),
                path("accounts/", include("allauth.urls")),
                path(
                    "accounts/social/connections/<int:pk>/delete/",
                    views.SocialAccountDeleteView.as_view(),
                    name="delete_social_account_by_pk",
                ),
                path("offline/", views.OfflineView.as_view(), name="offline"),
                path(
                    "invitations/send-invite/", views.InvitePerson.as_view(), name="invite_person"
                ),
                path(
                    "invitations/code/enter/",
                    views.EnterInvitationCode.as_view(),
                    name="enter_invitation_code",
                ),
                path(
                    "invitations/code/generate/",
                    views.GenerateInvitationCode.as_view(),
                    name="generate_invitation_code",
                ),
                path(
                    "invitations/disabled/",
                    views.InviteDisabledView.as_view(),
                    name="invite_disabled",
                ),
                path("invitations/", include("invitations.urls")),
                path("status/", views.SystemStatus.as_view(), name="system_status"),
                path("", include(tf_urls)),
                path("account/login/", views.TwoFactorLoginView.as_view()),
                path(
                    "account/two_factor/add/",
                    views.TwoFactorSetupView.as_view(),
                    name="setup_two_factor_auth",
                ),
                path("school_terms/", views.SchoolTermListView.as_view(), name="school_terms"),
                path(
                    "school_terms/create/",
                    views.SchoolTermCreateView.as_view(),
                    name="create_school_term",
                ),
                path(
                    "school_terms/<int:pk>/",
                    views.SchoolTermEditView.as_view(),
                    name="edit_school_term",
                ),
                path("persons/", views.persons, name="persons"),
                path(
                    "person/", TemplateView.as_view(template_name="core/empty.html"), name="person"
                ),
                path("persons/create/", views.CreatePersonView.as_view(), name="create_person"),
                path(
                    "persons/<int:id_>/",
                    TemplateView.as_view(template_name="core/empty.html"),
                    name="person_by_id",
                ),
                path(
                    "persons/<int:pk>/edit/",
                    views.EditPersonView.as_view(),
                    name="edit_person_by_id",
                ),
                path("persons/<int:id_>/delete/", views.delete_person, name="delete_person_by_id"),
                path(
                    "persons/<int:pk>/invite/",
                    views.InvitePersonByID.as_view(),
                    name="invite_person_by_id",
                ),
                path("groups/", views.groups, name="groups"),
                path(
                    "groups/additional_fields/", views.additional_fields, name="additional_fields"
                ),
                path("groups/child_groups/", views.groups_child_groups, name="groups_child_groups"),
                path(
                    "groups/additional_fields/<int:id_>/edit/",
                    views.edit_additional_field,
                    name="edit_additional_field_by_id",
                ),
                path(
                    "groups/additional_fields/create/",
                    views.edit_additional_field,
                    name="create_additional_field",
                ),
                path(
                    "groups/additional_fields/<int:id_>/delete/",
                    views.delete_additional_field,
                    name="delete_additional_field_by_id",
                ),
                path("groups/create/", views.edit_group, name="create_group"),
                path("groups/<int:id_>/", views.group, name="group_by_id"),
                path("groups/<int:id_>/edit/", views.edit_group, name="edit_group_by_id"),
                path("groups/<int:id_>/delete/", views.delete_group, name="delete_group_by_id"),
                path("", views.index, name="index"),
                path("dashboard/edit/", views.EditDashboardView.as_view(), name="edit_dashboard"),
                path("groups/group_types/create", views.edit_group_type, name="create_group_type"),
                path(
                    "groups/group_types/<int:id_>/delete/",
                    views.delete_group_type,
                    name="delete_group_type_by_id",
                ),
                path(
                    "groups/group_types/<int:id_>/edit/",
                    views.edit_group_type,
                    name="edit_group_type_by_id",
                ),
                path("groups/group_types/", views.group_types, name="group_types"),
                path("announcements/", views.announcements, name="announcements"),
                path("announcements/create/", views.announcement_form, name="add_announcement"),
                path(
                    "announcements/edit/<int:id_>/",
                    views.announcement_form,
                    name="edit_announcement",
                ),
                path(
                    "announcements/delete/<int:id_>/",
                    views.delete_announcement,
                    name="delete_announcement",
                ),
                path("search/searchbar/", views.searchbar_snippets, name="searchbar_snippets"),
                path("search/", views.PermissionSearchView.as_view(), name="haystack_search"),
                path("maintenance-mode/", include("maintenance_mode.urls")),
                path("impersonate/", include("impersonate.urls")),
                path(
                    "oauth/applications/",
                    views.OAuth2ListView.as_view(),
                    name="oauth2_applications",
                ),
                path(
                    "oauth/applications/register/",
                    views.OAuth2RegisterView.as_view(),
                    name="register_oauth_application",
                ),
                path(
                    "oauth/applications/<int:pk>/",
                    views.OAuth2DetailView.as_view(),
                    name="oauth2_application",
                ),
                path(
                    "oauth/applications/<int:pk>/delete/",
                    views.OAuth2DeleteView.as_view(),
                    name="delete_oauth2_application",
                ),
                path(
                    "oauth/applications/<int:pk>/edit/",
                    views.OAuth2EditView.as_view(),
                    name="edit_oauth2_application",
                ),
                path(
                    "oauth/authorize/",
                    views.CustomAuthorizationView.as_view(),
                    name="oauth2_provider:authorize",
                ),
                path("__i18n__/", include("django.conf.urls.i18n")),
                path(
                    "ckeditor/upload/",
                    permission_required("core.ckeditor_upload_files_rule")(
                        ckeditor_uploader_views.upload
                    ),
                    name="ckeditor_upload",
                ),
                path(
                    "ckeditor/browse/",
                    permission_required("core.ckeditor_upload_files_rule")(
                        ckeditor_uploader_views.browse
                    ),
                    name="ckeditor_browse",
                ),
                path("select2/", include("django_select2.urls")),
                path(
                    "calendarweek_i18n.js", calendarweek.django.i18n_js, name="calendarweek_i18n_js"
                ),
                path("gettext.js", JavaScriptCatalog.as_view(), name="javascript-catalog"),
                path(
                    "preferences/site/",
                    views.preferences,
                    {"registry_name": "site"},
                    name="preferences_site",
                ),
                path(
                    "preferences/person/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path(
                    "preferences/site/<int:pk>/",
                    views.preferences,
                    {"registry_name": "site"},
                    name="preferences_site",
                ),
                path(
                    "preferences/person/<int:pk>/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/<int:pk>/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path(
                    "preferences/site/<int:pk>/<str:section>/",
                    views.preferences,
                    {"registry_name": "site"},
                    name="preferences_site",
                ),
                path(
                    "preferences/person/<int:pk>/<str:section>/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/<int:pk>/<str:section>/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path(
                    "preferences/site/<str:section>/",
                    views.preferences,
                    {"registry_name": "site"},
                    name="preferences_site",
                ),
                path(
                    "preferences/person/<str:section>/",
                    views.preferences,
                    {"registry_name": "person"},
                    name="preferences_person",
                ),
                path(
                    "preferences/group/<str:section>/",
                    views.preferences,
                    {"registry_name": "group"},
                    name="preferences_group",
                ),
                path("health/", include(health_urls)),
                path("health/pdf/", views.TestPDFGenerationView.as_view(), name="test_pdf"),
                path(
                    "data_checks/",
                    views.DataCheckView.as_view(),
                    name="check_data",
                ),
                path(
                    "data_checks/run/",
                    views.RunDataChecks.as_view(),
                    name="data_check_run",
                ),
                path(
                    "data_checks/<int:pk>/<str:solve_option>/",
                    views.SolveDataCheckView.as_view(),
                    name="data_check_solve",
                ),
                path(
                    "dashboard_widgets/",
                    views.DashboardWidgetListView.as_view(),
                    name="dashboard_widgets",
                ),
                path(
                    "dashboard_widgets/<int:pk>/edit/",
                    views.DashboardWidgetEditView.as_view(),
                    name="edit_dashboard_widget",
                ),
                path(
                    "dashboard_widgets/<int:pk>/delete/",
                    views.DashboardWidgetDeleteView.as_view(),
                    name="delete_dashboard_widget",
                ),
                path(
                    "dashboard_widgets/<str:app>/<str:model>/new/",
                    views.DashboardWidgetCreateView.as_view(),
                    name="create_dashboard_widget",
                ),
                path(
                    "dashboard_widgets/default/",
                    views.EditDashboardView.as_view(),
                    {"default": True},
                    name="edit_default_dashboard",
                ),
                path(
                    "permissions/global/user/",
                    views.UserGlobalPermissionsListBaseView.as_view(),
                    name="manage_user_global_permissions",
                ),
                path(
                    "permissions/global/group/",
                    views.GroupGlobalPermissionsListBaseView.as_view(),
                    name="manage_group_global_permissions",
                ),
                path(
                    "permissions/object/user/",
                    views.UserObjectPermissionsListBaseView.as_view(),
                    name="manage_user_object_permissions",
                ),
                path(
                    "permissions/object/group/",
                    views.GroupObjectPermissionsListBaseView.as_view(),
                    name="manage_group_object_permissions",
                ),
                path(
                    "permissions/global/user/<int:pk>/delete/",
                    views.UserGlobalPermissionDeleteView.as_view(),
                    name="delete_user_global_permission",
                ),
                path(
                    "permissions/global/group/<int:pk>/delete/",
                    views.GroupGlobalPermissionDeleteView.as_view(),
                    name="delete_group_global_permission",
                ),
                path(
                    "permissions/object/user/<int:pk>/delete/",
                    views.UserObjectPermissionDeleteView.as_view(),
                    name="delete_user_object_permission",
                ),
                path(
                    "permissions/object/group/<int:pk>/delete/",
                    views.GroupObjectPermissionDeleteView.as_view(),
                    name="delete_group_object_permission",
                ),
                path(
                    "permissions/assign/",
                    views.SelectPermissionForAssignView.as_view(),
                    name="select_permission_for_assign",
                ),
                path(
                    "permissions/<int:pk>/assign/",
                    views.AssignPermissionView.as_view(),
                    name="assign_permission",
                ),
            ]
        ),
    ),
    path("admin/", admin.site.urls),
    path("admin/uwsgi/", include("django_uwsgi.urls")),
]

# Use custom server error handler to get a request object in the template
handler500 = views.server_error

# Add URLs for optional features
if hasattr(settings, "TWILIO_ACCOUNT_SID"):
    from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls  # noqa

    urlpatterns += [path("django/", include(tf_twilio_urls))]

# Automatically mount URLs from all installed AlekSIS apps
for app_config in apps.app_configs.values():
    if not app_config.name.startswith("aleksis.apps."):
        continue

    try:
        urls_module = import_module(f"{app_config.name}.urls")
    except ModuleNotFoundError:
        # Ignore exception as app just has no URLs
        urls_module = None

    if hasattr(urls_module, "urlpatterns"):
        urlpatterns.append(
            path(f"django/app/{app_config.label}/", include(urls_module.urlpatterns))
        )

    if hasattr(urls_module, "api_urlpatterns"):
        urlpatterns.append(path(f"app/{app_config.label}/", include(urls_module.api_urlpatterns)))

urlpatterns.append(
    re_path(
        r"^(?P<url>.*)/$", TemplateView.as_view(template_name="core/vue_index.html"), name="vue_app"
    )
)
