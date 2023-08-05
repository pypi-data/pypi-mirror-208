<template>
  <v-list-item>
    <v-list-item-icon>
      <v-icon color="grey darken-2" x-large>{{ icon }}</v-icon>
    </v-list-item-icon>
    <v-list-item-content>
      <v-list-item-title class="font-weight-medium"
        ><slot name="title"
      /></v-list-item-title>
      <slot name="subtitles" />
    </v-list-item-content>
    <v-list-item-action>
      <slot name="action" />
    </v-list-item-action>
  </v-list-item>
</template>

<script>
export default {
  name: "TwoFactorDeviceBase",
  props: {
    icon: {
      type: String,
      required: true,
    },
  },
};
</script>
