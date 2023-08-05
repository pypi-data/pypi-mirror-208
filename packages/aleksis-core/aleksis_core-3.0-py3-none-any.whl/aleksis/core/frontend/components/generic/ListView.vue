<template>
  <detail-view no-avatar>
    <template #title>
      <slot name="title" />
    </template>

    <template #actions>
      <slot name="actions" />
    </template>

    <slot name="filter" />
    <slot />
  </detail-view>
</template>

<script>
import DetailView from "./DetailView.vue";
export default {
  name: "ListView",
  components: {
    DetailView,
  },
};
</script>

<style scoped></style>
