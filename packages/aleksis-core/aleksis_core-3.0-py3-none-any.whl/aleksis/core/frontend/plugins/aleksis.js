/*
 * Plugin to collect AlekSIS-specific Vue utilities.
 */

// aleksisAppImporter is a virtual module defined in Vite config
import { appMessages } from "aleksisAppImporter";
import aleksisMixin from "../mixins/aleksis.js";

console.debug("Defining AleksisVue plugin");
const AleksisVue = {};

AleksisVue.install = function (Vue) {
  /*
   * The browser title when the app was loaded.
   *
   * Thus, it is injected from Django in the vue_index template.
   */
  Vue.$pageBaseTitle = document.title;

  Vue.$aleksisFrontendSettings = JSON.parse(
    document.getElementById("frontend_settings").textContent
  );

  /**
   * Configure Sentry if desired.
   *
   * It depends on Sentry settings being passed as a DOM object by Django
   * in the vue_index template.
   */
  Vue.$configureSentry = function (router) {
    if (Vue.$aleksisFrontendSettings.sentry.enabled) {
      import("../app/sentry.js").then((mod) => {
        mod.default.Sentry.init({
          Vue,
          dsn: Vue.$aleksisFrontendSettings.sentry.dsn,
          environment: Vue.$aleksisFrontendSettings.sentry.environment,
          tracesSampleRate:
            Vue.$aleksisFrontendSettings.sentry.traces_sample_rate,
          logError: true,
          integrations: [
            new mod.default.BrowserTracing({
              routingInstrumentation:
                mod.default.Sentry.vueRouterInstrumentation(router),
            }),
          ],
        });
      });
    }
  };

  /**
   * Register all global components that shall be reusable by apps.
   */
  Vue.$registerGlobalComponents = function () {
    Vue.component("MessageBox", () =>
      import("../components/generic/MessageBox.vue")
    );
    Vue.component("SmallContainer", () =>
      import("../components/generic/SmallContainer.vue")
    );
    Vue.component("BackButton", () =>
      import("../components/generic/BackButton.vue")
    );
    Vue.component("AvatarClickbox", () =>
      import("../components/generic/AvatarClickbox.vue")
    );
    Vue.component("DetailView", () =>
      import("../components/generic/DetailView.vue")
    );
    Vue.component("ListView", () =>
      import("../components/generic/ListView.vue")
    );
    Vue.component("ButtonMenu", () =>
      import("../components/generic/ButtonMenu.vue")
    );
    Vue.component("ErrorPage", () => import("../components/app/ErrorPage.vue"));
  };

  /**
   * Set the page title.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string} title Specific title to set, or null.
   * @param {Object} route Route to discover title from, or null.
   */
  Vue.prototype.$setPageTitle = function (title, route) {
    let titleParts = [];

    if (title) {
      titleParts.push(title);
    } else {
      if (!route) {
        route = this.$route;
      }
      if (route.meta.titleKey) {
        titleParts.push(this.$t(route.meta.titleKey));
      }
    }

    titleParts.push(Vue.$pageBaseTitle);
    const newTitle = titleParts.join(" – ");
    console.debug(`Setting page title: ${newTitle}`);
    document.title = newTitle;
  };

  /**
   * Load i18n messages from all known AlekSIS apps.
   */
  Vue.prototype.$loadAppMessages = function () {
    for (const messages of Object.values(appMessages)) {
      for (let locale in messages) {
        this.$i18n.mergeLocaleMessage(locale, messages[locale]);
      }
    }
  };

  /**
   * Invalidate state and force reload from server.
   *
   * Mostly useful after the user context changes by login/logout/impersonate.
   */
  Vue.prototype.$invalidateState = function () {
    console.info("Invalidating application state");

    this.invalidation = true;

    this.$apollo
      .getClient()
      .resetStore()
      .then(
        () => {
          console.info("GraphQL cache cleared");
          this.invalidation = false;
        },
        (error) => {
          console.error("Could not clear GraphQL cache:", error);
          this.invalidation = false;
        }
      );
  };

  /**
   * Add navigation guards to account for global loading state and page titles.
   */
  Vue.prototype.$setupNavigationGuards = function () {
    const vm = this;

    // eslint-disable-next-line no-unused-vars
    this.$router.afterEach((to, from, next) => {
      console.debug("Setting new page title due to route change");
      vm.$setPageTitle(null, to);
    });

    // eslint-disable-next-line no-unused-vars
    this.$router.beforeEach((to, from, next) => {
      vm.contentLoading = true;
      next();
    });

    // eslint-disable-next-line no-unused-vars
    this.$router.afterEach((to, from) => {
      if (vm.isLegacyBaseTemplate) {
        // Skip resetting loading state for legacy pages
        // as they are probably not finished with loading yet
        // LegacyBaseTemplate will reset the loading state later
        return;
      }
      vm.contentLoading = false;
    });

    // eslint-disable-next-line no-unused-vars
    this.$router.beforeEach((to, from, next) => {
      if (from.meta.invalidate === "leave" || to.meta.invalidate === "enter") {
        console.debug("Route requests to invalidate state");
        vm.$invalidateState();
      }
      next();
    });
  };

  // Add default behaviour for all components
  Vue.mixin(aleksisMixin);
};

export default AleksisVue;
