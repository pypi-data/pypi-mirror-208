<template>
  <v-menu transition="slide-y-transition" offset-y>
    <template #activator="{ on, attrs }">
      <slot name="activator" v-bind="{ on, attrs }">
        <v-btn outlined text v-bind="attrs" v-on="on">
          <v-icon center>
            {{ icon }}
          </v-icon>
        </v-btn>
      </slot>
    </template>

    <v-list>
      <slot />
    </v-list>
  </v-menu>
</template>

<script>
export default {
  name: "ButtonMenu",
  props: {
    icon: {
      type: String,
      required: false,
      default: "mdi-dots-horizontal",
    },
  },
};
</script>

<style scoped></style>
