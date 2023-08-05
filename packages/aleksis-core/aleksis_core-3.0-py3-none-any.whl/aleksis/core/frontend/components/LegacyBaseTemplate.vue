<!--
  Base component to load legacy views from Django.

  It loads the legacy view into an iframe and attaches some utility
  code to it. The legacy application and the new Vue application can
  communicate with each other through a message channel.

  This helps during the migration from the pure SSR Django application
  in AlekSIS 2.x to the pure Vue and GraphQL based application.
  It will be removed once legacy view get unsupported.
-->

<template>
  <message-box
    v-if="
      !byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate
    "
    type="error"
  >
    {{ $t("legacy.unworthy") }}
  </message-box>
  <iframe
    v-else
    :src="'/django' + $route.path + queryString"
    :height="iFrameHeight + 'px'"
    class="iframe-fullsize"
    @load="load"
    ref="contentIFrame"
  ></iframe>
</template>

<script>
export default {
  props: {
    byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate:
      {
        type: Boolean,
        required: true,
      },
  },
  data: function () {
    return {
      iFrameHeight: 0,
    };
  },
  computed: {
    queryString() {
      let qs = [];
      for (const [param, value] of Object.entries(this.$route.query)) {
        qs.push(`${param}=${encodeURIComponent(value)}`);
      }
      return "?" + qs.join("&");
    },
  },
  methods: {
    /** Handle iframe data after inner page loaded */
    load() {
      // Write new location of iframe back to Vue Router
      const location = this.$refs.contentIFrame.contentWindow.location;
      const url = new URL(location);
      const path = url.pathname.replace(/^\/django/, "");
      const pathWithQueryString = path + encodeURI(url.search);
      const routePath =
        path.charAt(path.length - 1) === "/" &&
        this.$route.path.charAt(path.length - 1) !== "/"
          ? this.$route.path + "/"
          : this.$route.path;
      if (path !== routePath) {
        this.$router.push(pathWithQueryString);
      }

      // Show loader if iframe starts to change its content, even if the $route stays the same
      this.$refs.contentIFrame.contentWindow.onpagehide = () => {
        this.$root.contentLoading = true;
      };

      // Write title of iframe to SPA window
      const title = this.$refs.contentIFrame.contentWindow.document.title;
      this.$root.$setPageTitle(title);

      // Adapt height of IFrame according to the height of its contents once and observe height changes
      if (
        this.$refs.contentIFrame.contentDocument &&
        this.$refs.contentIFrame.contentDocument.body
      ) {
        this.iFrameHeight =
          this.$refs.contentIFrame.contentDocument.body.scrollHeight;
        new ResizeObserver(() => {
          if (
            this.$refs.contentIFrame &&
            this.$refs.contentIFrame.contentDocument &&
            this.$refs.contentIFrame.contentDocument.body
          ) {
            this.iFrameHeight =
              this.$refs.contentIFrame.contentDocument.body.scrollHeight;
          }
        }).observe(this.$refs.contentIFrame.contentDocument.body);
      }

      this.$root.contentLoading = false;
    },
  },
  watch: {
    $route() {
      // Show loading animation once route changes
      this.$root.contentLoading = true;

      // Scroll to top only when route changes to not affect form submits etc.
      // A small duration to avoid flashing of the UI
      this.$vuetify.goTo(0, { duration: 10 });
    },
  },
  name: "LegacyBaseTemplate",
};
</script>

<style scoped>
.iframe-fullsize {
  border: 0;
  width: calc(100% + 24px);
  margin: -12px;
}
</style>
