/*
 * Main entrypoint of AlekSIS0-Core.
 *
 * This script sets up all necessary Vue plugins and defines the Vue app.
 */

import Vue from "vue";
import Vuetify from "@/vuetify";
import VueI18n from "@/vue-i18n";
import VueRouter from "@/vue-router";
import VueApollo from "@/vue-apollo";
import VueCookies from "@/vue-cookies";

import AleksisVue from "./plugins/aleksis.js";

console.info("🎒 Welcome to AlekSIS®, the Free School Information System!");
console.info(
  "AlekSIS® is Free Software, licenced under the EUPL, version 1.2 or later, by Teckids e.V. (Bonn, Germany)"
);

// Install the AleksisVue plugin first and let it do early setup
Vue.use(AleksisVue);
Vue.$registerGlobalComponents();

// Third-party plugins
Vue.use(Vuetify);
Vue.use(VueI18n);
Vue.use(VueRouter);
Vue.use(VueApollo);
Vue.use(VueCookies);

// All of these imports yield config objects to be passed to the plugin constructors
import vuetifyOpts from "./app/vuetify.js";
import i18nOpts from "./app/i18n.js";
import routerOpts from "./app/router.js";
import apolloOpts from "./app/apollo.js";

const i18n = new VueI18n({
  locale: Vue.$cookies.get("django_language")
    ? Vue.$cookies.get("django_language")
    : "en",
  ...i18nOpts,
});
const vuetify = new Vuetify({
  lang: {
    current: Vue.$cookies.get("django_language")
      ? Vue.$cookies.get("django_language")
      : "en",
  },
  ...vuetifyOpts,
});
const router = new VueRouter(routerOpts);
const apolloProvider = new VueApollo(apolloOpts);

// Let AlekSIS plugin initialise Sentry
Vue.$configureSentry(router);

// Parent component rendering the UI and all features outside the specific pages
import App from "./components/app/App.vue";

const app = new Vue({
  el: "#app",
  apolloProvider,
  vuetify: vuetify,
  render: (h) => h(App),
  data: () => ({
    showCacheAlert: false,
    contentLoading: true,
    offline: false,
    backgroundActive: true,
    invalidation: false,
    snackbarItems: [],
  }),
  computed: {
    matchedComponents() {
      if (this.$route.matched.length > 0) {
        return this.$route.matched.map(
          (route) => route.components.default.name
        );
      }
      return [];
    },
    isLegacyBaseTemplate() {
      return this.matchedComponents.includes("LegacyBaseTemplate");
    },
  },
  router,
  i18n,
});

// Late setup for some plugins handed off to out ALeksisVue plugin
app.$loadAppMessages();
app.$setupNavigationGuards();
