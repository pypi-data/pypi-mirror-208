/**
 * Vue mixin containing code setting error 404 status.
 *
 * Only used by main App component, but factored out for readability.
 */

const error404Mixin = {
  methods: {
    set404() {
      if (this.$route.matched.length === 0) {
        this.error404 = true;
        this.$root.contentLoading = false;
      } else {
        this.error404 = false;
      }
    },
  },
  mounted() {
    this.$router.onReady(this.set404);
    this.$router.afterEach((to, from) => {
      this.set404();
    });
  },
};

export default error404Mixin;
