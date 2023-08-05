<template>
  <div class="fullsize">
    <template v-if="$apollo.queries.person.loading">
      <v-row class="fill-height ma-0" align="center" justify="center">
        <v-progress-circular
          indeterminate
          color="grey lighten-5"
        ></v-progress-circular>
      </v-row>
    </template>
    <v-img
      v-if="person && person.image"
      :src="person.image"
      :alt="$t('person.avatar')"
      max-width="100%"
      max-height="100%"
      :contain="contain"
      class="fullsize"
    />
    <v-icon class="grey lighten-1" dark v-else>mdi-folder</v-icon>
  </div>
</template>

<script>
import gqlAvatarContent from "./avatarContent.graphql";
export default {
  name: "AvatarContent",
  props: {
    id: {
      type: String,
      required: false,
      default: "",
    },
    contain: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  apollo: {
    person: {
      query: gqlAvatarContent,
      variables() {
        return {
          id: this.id,
        };
      },
    },
  },
};
</script>

<style scoped></style>
