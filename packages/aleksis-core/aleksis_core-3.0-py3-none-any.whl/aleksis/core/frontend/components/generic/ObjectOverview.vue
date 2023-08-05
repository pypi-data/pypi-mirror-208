<template>
  <div>
    <slot name="loading" v-if="$apollo.queries.object.loading"></slot>
    <slot v-else-if="object" v-bind="object"></slot>
    <error-page
      v-else
      :short-error-message-key="shortErrorMessageKey"
      :long-error-message-key="longErrorMessageKey"
      :redirect-button-text-key="redirectButtonTextKey"
      :redirect-route-name="redirectRouteName"
      :redirect-button-icon="redirectButtonIcon"
    />
  </div>
</template>

<script>
export default {
  name: "ObjectOverview",
  props: {
    titleAttr: {
      type: String,
      required: true,
    },
    query: {
      type: Object,
      required: true,
    },
    shortErrorMessageKey: {
      type: String,
      required: false,
      default: "network_errors.error_404",
    },
    longErrorMessageKey: {
      type: String,
      required: false,
      default: "network_errors.page_not_found",
    },
    redirectButtonTextKey: {
      type: String,
      required: false,
      default: "network_errors.back_to_start",
    },
    redirectRouteName: {
      type: String,
      required: false,
      default: "dashboard",
    },
    redirectButtonIcon: {
      type: String,
      required: false,
      default: "mdi-home-outline",
    },
  },
  methods: {
    getTitleAttr(obj) {
      let tmpObj = obj;
      this.titleAttr.split(".").forEach((attr) => {
        tmpObj = tmpObj[attr];
      });
      return tmpObj;
    },
  },
  apollo: {
    object() {
      return {
        query: this.query,
        variables() {
          if (this.$route.params.id) {
            return {
              id: this.$route.params.id,
            };
          }
          return {};
        },
        result({ data }) {
          if (data && data.object) {
            this.$root.$setPageTitle(this.getTitleAttr(data.object));
          }
        },
        error() {},
      };
    },
  },
};
</script>

<style scoped></style>
