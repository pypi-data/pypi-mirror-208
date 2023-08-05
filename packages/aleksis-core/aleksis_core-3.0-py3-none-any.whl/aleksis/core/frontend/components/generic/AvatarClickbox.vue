<template>
  <v-dialog v-model="overlay" max-width="fit-content" max-height="fit-content">
    <template #activator="{ on, attrs }">
      <v-card class="rounded-circle">
        <v-responsive :aspect-ratio="1" v-bind="attrs" v-on="on">
          <slot name="activator" />
        </v-responsive>
      </v-card>
    </template>
    <div class="inDialog">
      <slot class="inDialog" />
    </div>
  </v-dialog>
</template>

<script>
export default {
  name: "AvatarClickBox",
  data: () => ({
    overlay: false,
  }),
};
</script>

<style scoped>
.inDialog {
  /* FIXME: find a way to enlarge image */
  max-height: 80vmin;
  width: 80vmin;
}
</style>
