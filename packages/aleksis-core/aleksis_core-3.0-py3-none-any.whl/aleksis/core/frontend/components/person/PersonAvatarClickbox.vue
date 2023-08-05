<template>
  <avatar-clickbox>
    <template #activator>
      <avatar-content :id="id" class="rounded-circle" />
    </template>
    <avatar-content :id="id" contain />
  </avatar-clickbox>
</template>

<script>
import AvatarContent from "./AvatarContent.vue";

export default {
  name: "PersonAvatarClickBox",
  components: {
    AvatarContent,
  },
  data: () => ({
    overlay: false,
  }),
  props: {
    id: {
      type: String,
      required: false,
      default: "",
    },
  },
};
</script>

<style scoped></style>
