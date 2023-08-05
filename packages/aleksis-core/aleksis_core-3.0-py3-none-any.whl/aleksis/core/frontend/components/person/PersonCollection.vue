<template>
  <v-list v-if="persons.length">
    <v-list-item
      v-for="person in persons"
      :key="person.id"
      :to="{ name: 'core.personById', params: { id: person.id } }"
    >
      <v-list-item-avatar>
        <avatar-content :id="person.id" />
      </v-list-item-avatar>

      <v-list-item-content>
        <v-list-item-title>{{ person.fullName }}</v-list-item-title>
      </v-list-item-content>
    </v-list-item>
  </v-list>
  <p v-else>
    {{ $t("person.no_persons") }}
  </p>
</template>

<script>
import AvatarContent from "./AvatarContent.vue";

export default {
  name: "PersonList",
  components: { AvatarContent },
  props: {
    persons: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped></style>
