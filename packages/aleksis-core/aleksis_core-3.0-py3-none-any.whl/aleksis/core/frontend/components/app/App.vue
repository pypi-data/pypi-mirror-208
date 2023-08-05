<!--
  Main App component.

  This component contains the outer app UI of AlekSIS and all behaviour
  that is always on-screen, independent of the specific page.
-->

<template>
  <v-app v-cloak>
    <splash v-if="$apollo.loading && !systemProperties" splash />
    <div v-else>
      <side-nav
        v-model="drawer"
        :system-properties="systemProperties"
        :side-nav-menu="sideNavMenu"
      ></side-nav>
      <v-app-bar
        app
        :color="$vuetify.theme.dark ? undefined : 'primary white--text'"
      >
        <v-app-bar-nav-icon @click="drawer = !drawer" color="white" />

        <v-toolbar-title
          tag="a"
          class="white--text text-decoration-none"
          @click="$router.push({ name: 'dashboard' })"
        >
          {{ systemProperties.sitePreferences.generalTitle }}
        </v-toolbar-title>

        <v-progress-linear
          :active="$root.contentLoading"
          :indeterminate="$root.contentLoading"
          absolute
          bottom
          :color="$vuetify.theme.dark ? 'primary' : 'grey lighten-3'"
        ></v-progress-linear>

        <v-spacer />
        <v-btn
          icon
          color="white"
          v-if="needRefresh && refreshDismissed"
          @click="refreshDismissed = false"
        >
          <v-icon>mdi-update</v-icon>
        </v-btn>
        <div
          v-if="whoAmI && whoAmI.isAuthenticated && whoAmI.person"
          class="d-flex"
        >
          <notification-list v-if="!whoAmI.person.isDummy" />
          <account-menu
            :account-menu="accountMenu"
            :system-properties="systemProperties"
            :who-am-i="whoAmI"
          ></account-menu>
        </div>
      </v-app-bar>
      <v-main>
        <v-container>
          <message-box type="warning" v-if="$root.offline">
            {{ $t("network_errors.offline_notification") }}
          </message-box>

          <message-box
            type="error"
            v-if="whoAmI && whoAmI.person && whoAmI.person.isDummy"
          >
            {{ $t("base.person_is_dummy") }}
          </message-box>
          <message-box
            type="error"
            v-else-if="whoAmI && !whoAmI.person && !whoAmI.isAnonymous"
          >
            {{ $t("base.user_not_linked_to_person") }}
          </message-box>

          <div v-if="messages">
            <message-box
              v-for="(message, idx) in messages"
              :type="message.tags"
              :key="idx"
              >{{ message.message }}
            </message-box>
          </div>

          <error-page
            v-if="error404"
            short-error-message-key="network_errors.error_404"
            long-error-message-key="network_errors.page_not_found"
            redirect-button-text-key="network_errors.back_to_start"
            redirect-route-name="dashboard"
            redirect-button-icon="mdi-home-outline"
          >
          </error-page>
          <router-view
            v-else-if="
              !$route.meta.permission ||
              checkPermission($route.meta.permission) ||
              $route.name === 'dashboard'
            "
            @mounted="routeComponentMounted"
          />
          <error-page
            v-else-if="
              whoAmI &&
              !$apollo.queries.whoAmI.loading &&
              !checkPermission($route.meta.permission)
            "
            short-error-message-key="base.no_permission_message_short"
            long-error-message-key="base.no_permission_message_long"
            redirect-button-text-key="base.no_permission_redirect_text"
            redirect-route-name="core.account.login"
            redirect-button-icon="mdi-login-variant"
          >
          </error-page>
        </v-container>
      </v-main>

      <celery-progress-bottom v-if="whoAmI && !whoAmI.isAnonymous" />

      <v-footer
        app
        absolute
        inset
        dark
        class="pa-0 d-flex"
        color="primary lighten-1"
      >
        <v-card flat tile class="primary white--text flex-grow-1">
          <div v-if="footerMenu && footerMenu.items">
            <v-card-text class="pa-0">
              <v-container class="px-6">
                <v-row justify="center" no-gutters>
                  <v-btn
                    v-for="menu_item in footerMenu.items"
                    :key="menu_item.name"
                    text
                    rounded
                    :href="menu_item.url"
                    color="white"
                    class="ma-2"
                  >
                    <v-icon v-if="menu_item.icon" left>{{
                      "mdi-" + menu_item.icon
                    }}</v-icon>
                    {{ menu_item.name }}
                  </v-btn>
                </v-row>
              </v-container>
            </v-card-text>
            <v-divider />
          </div>

          <v-card-text class="pa-0">
            <v-container class="px-6">
              <v-row>
                <v-col class="white--text d-flex align-center subtitle-2">
                  <div>
                    <router-link
                      :to="{ name: 'core.about' }"
                      class="white--text text-decoration-none"
                      >{{ $t("base.about_aleksis") }}
                    </router-link>
                    <!-- eslint-disable-next-line -->
                    <span>© The AlekSIS Team</span>
                  </div>
                </v-col>
                <v-col class="d-flex justify-end">
                  <v-btn
                    v-if="systemProperties.sitePreferences.footerImprintUrl"
                    small
                    text
                    :href="systemProperties.sitePreferences.footerImprintUrl"
                    color="white"
                  >
                    {{ $t("base.imprint") }}
                  </v-btn>
                  <v-btn
                    v-if="systemProperties.sitePreferences.footerPrivacyUrl"
                    small
                    text
                    :href="systemProperties.sitePreferences.footerPrivacyUrl"
                    color="white"
                  >
                    {{ $t("base.privacy_policy") }}
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
        </v-card>
      </v-footer>
    </div>
    <snackbar-item
      v-for="item in $root.snackbarItems"
      :key="item.id"
      :snackbar-item="item"
    />
    <v-snackbar v-model="needRefresh" v-if="!refreshDismissed" timeout="-1">
      {{ $t("service_worker.new_version_available") }}

      <template #action="{ attrs }">
        <v-btn color="primary" text @click="updateServiceWorker()">
          {{ $t("service_worker.update") }}
        </v-btn>
        <v-btn color="primary" text @click="refreshDismissed = true">
          {{ $t("service_worker.dismiss") }}
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import AccountMenu from "./AccountMenu.vue";
import NotificationList from "../notifications/NotificationList.vue";
import CeleryProgressBottom from "../celery_progress/CeleryProgressBottom.vue";
import Splash from "./Splash.vue";
import SideNav from "./SideNav.vue";
import SnackbarItem from "./SnackbarItem.vue";
import ErrorPage from "./ErrorPage.vue";

import gqlWhoAmI from "./whoAmI.graphql";
import gqlMessages from "./messages.graphql";
import gqlSystemProperties from "./systemProperties.graphql";

import useRegisterSWMixin from "../../mixins/useRegisterSW";
import offlineMixin from "../../mixins/offline";
import menusMixin from "../../mixins/menus";
import routesMixin from "../../mixins/routes";
import error404Mixin from "../../mixins/error404";

export default {
  data() {
    return {
      drawer: this.$vuetify.breakpoint.lgAndUp,
      whoAmI: null,
      systemProperties: null,
      messages: null,
      error404: false,
    };
  },
  apollo: {
    systemProperties: gqlSystemProperties,
    whoAmI: {
      query: gqlWhoAmI,
      variables() {
        return {
          permissions: this.permissionNames,
        };
      },
      pollInterval: 10000,
    },
    messages: {
      query: gqlMessages,
    },
  },
  methods: {
    routeComponentMounted() {
      if (!this.$root.isLegacyBaseTemplate) {
        this.$root.contentLoading = false;
      }
    },
  },
  watch: {
    systemProperties: function (newProperties) {
      this.$vuetify.theme.themes.light.primary =
        newProperties.sitePreferences.themePrimary;
      this.$vuetify.theme.themes.light.secondary =
        newProperties.sitePreferences.themeSecondary;
      this.$vuetify.theme.themes.dark.primary =
        newProperties.sitePreferences.themePrimary;
      this.$vuetify.theme.themes.dark.secondary =
        newProperties.sitePreferences.themeSecondary;
    },
    whoAmI: {
      handler() {
        this.buildMenus();
      },
      deep: true,
    },
    $route: {
      handler(newRoute) {
        if (this.$apollo.queries.messages) {
          this.$apollo.queries.messages.refetch();
        }
      },
      immediate: true,
    },
  },
  name: "App",
  components: {
    AccountMenu,
    ErrorPage,
    NotificationList,
    CeleryProgressBottom,
    Splash,
    SideNav,
    SnackbarItem,
  },
  mixins: [
    useRegisterSWMixin,
    offlineMixin,
    menusMixin,
    routesMixin,
    error404Mixin,
  ],
};
</script>

<style scoped></style>
