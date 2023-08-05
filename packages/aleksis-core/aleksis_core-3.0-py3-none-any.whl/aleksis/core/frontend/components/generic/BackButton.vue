<template>
  <v-btn color="secondary" v-bind="$attrs">
    <v-icon left>mdi-chevron-left</v-icon>
    {{ $t("actions.back") }}
  </v-btn>
</template>

<script>
export default {
  name: "BackButton",
};
</script>
