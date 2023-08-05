<template>
  <v-list v-if="groups.length">
    <v-list-item
      v-for="group in groups"
      :key="group.id"
      :to="{ name: 'core.group', params: { id: group.id } }"
    >
      <v-list-item-content>
        <v-list-item-title>
          {{ group.name }}
          <span v-if="group.schoolTerm && group.schoolTerm.name">
            ({{ group.schoolTerm.name }})
          </span>
        </v-list-item-title>
      </v-list-item-content>
    </v-list-item>
  </v-list>
  <p v-else>
    {{ $t("person.no_persons") }}
  </p>
</template>

<script>
export default {
  name: "GroupList",
  props: {
    groups: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped></style>
