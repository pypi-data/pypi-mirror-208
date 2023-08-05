/*
 * Configuration for Vuetify
 */

import "@/@mdi/font/css/materialdesignicons.css";
import "@/vuetify/dist/vuetify.min.css";
import "../css/global.scss";

const vuetifyOpts = {
  icons: {
    iconfont: "mdi", // default - only for display purposes
    values: {
      cancel: "mdi-close-circle-outline",
      delete: "mdi-close-circle-outline",
      success: "mdi-check-circle-outline",
      info: "mdi-information-outline",
      warning: "mdi-alert-outline",
      error: "mdi-alert-octagon-outline",
      prev: "mdi-chevron-left",
      next: "mdi-chevron-right",
      checkboxOn: "mdi-checkbox-marked-outline",
      checkboxIndeterminate: "mdi-minus-box-outline",
      edit: "mdi-pencil-outline",
      preferences: "mdi-cog-outline",
    },
  },
};

export default vuetifyOpts;
