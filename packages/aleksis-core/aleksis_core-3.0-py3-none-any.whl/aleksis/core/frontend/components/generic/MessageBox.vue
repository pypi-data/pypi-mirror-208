<script>
export default {
  name: "MessageBox",
  // Due to this component being a wrapper to a v-alert, all props of this can be used (and overridden).
};
</script>

<template>
  <v-alert border="left" text v-bind="$attrs">
    <slot></slot>
  </v-alert>
</template>
