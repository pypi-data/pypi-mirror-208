<template>
  <v-autocomplete
    :prepend-icon="'mdi-magnify'"
    append-icon=""
    @click:prepend="$router.push(`/search/?q=${q}`)"
    @keydown.enter="$router.push(`/search/?q=${q}`)"
    single-line
    clearable
    :loading="$apollo.queries.searchSnippets.loading"
    id="search"
    type="search"
    enterkeyhint="search"
    :label="$t('actions.search')"
    :search-input.sync="q"
    flat
    solo
    cache-items
    hide-no-data
    hide-details
    menu-props="closeOnContentClick"
    :items="searchSnippets"
  >
    <template #item="{ item }">
      <v-list-item @click="$router.push(item.obj.absoluteUrl.substring(7))">
        <v-list-item-icon v-if="item.obj.icon">
          <v-icon>{{ "mdi-" + item.obj.icon }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title> {{ item.obj.name }}</v-list-item-title>
          <v-list-item-subtitle>{{ item.text }}</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-autocomplete>
</template>

<script>
import gqlSearchSnippets from "./searchSnippets.graphql";

export default {
  name: "SidenavSearch",
  data() {
    return {
      q: "",
    };
  },
  apollo: {
    searchSnippets: {
      query: gqlSearchSnippets,
      variables() {
        return {
          q: this.q,
        };
      },
      skip() {
        return !this.q;
      },
      fetchPolicy: "network-only",
    },
  },
};
</script>
