<template>
  <v-snackbar
    v-model="visible"
    :color="snackbarItem.color"
    :timeout="snackbarItem.timeout"
    @input="deleteSnackbarItem"
  >
    {{ $t(snackbarItem.messageKey) }}
    <template #action="{ attrs }">
      <v-btn icon @click="deleteSnackbarItem"
        ><v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script>
export default {
  name: "SnackbarItem",
  data() {
    return {
      visible: true,
    };
  },
  props: {
    snackbarItem: {
      type: Object,
      required: true,
    },
  },
  methods: {
    deleteSnackbarItem() {
      this.$root.snackbarItems = this.$root.snackbarItems.filter(
        (obj) => obj.id !== this.snackbarItem.id
      );
    },
  },
};
</script>
