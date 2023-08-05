<template>
  <ApolloMutation
    v-if="dialogOpen"
    :mutation="gqlMutation"
    :variables="{ id: item.id }"
    :update="update"
    @done="close(true)"
  >
    <template #default="{ mutate, loading, error }">
      <v-dialog v-model="dialogOpen" max-width="500px">
        <v-card>
          <v-card-title class="text-h5">
            <slot name="title">
              {{ $t("actions.confirm_deletion") }}
            </slot>
          </v-card-title>
          <v-card-text>
            <slot name="body">
              <p class="text-body-1">{{ nameOfObject }}</p>
            </slot>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="close(false)" :disabled="loading">
              <slot name="cancelContent">
                {{ $t("actions.cancel") }}
              </slot>
            </v-btn>
            <v-btn
              color="error"
              text
              @click="mutate"
              :loading="loading"
              :disabled="loading"
            >
              <slot name="deleteContent">
                {{ $t("actions.delete") }}
              </slot>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-snackbar :value="error !== null">
        {{ error }}

        <template #action="{ attrs }">
          <v-btn color="primary" text v-bind="attrs" @click="error = null" icon>
            <v-icon>$close</v-icon>
          </v-btn>
        </template>
      </v-snackbar>
    </template>
  </ApolloMutation>
</template>

<script>
export default {
  name: "DeleteDialog",
  computed: {
    nameOfObject() {
      return this.itemAttribute in this.item || {}
        ? this.item[this.itemAttribute]
        : this.item.toString();
    },
    dialogOpen: {
      get() {
        return this.value;
      },

      set(val) {
        this.$emit("input", val);
      },
    },
  },
  methods: {
    update(store) {
      if (!this.gqlQuery) {
        // There is no GraphQL query to update
        return;
      }

      // Read the data from cache for query
      const storedData = store.readQuery({ query: this.gqlQuery });

      if (!storedData) {
        // There are no data in the cache yet
        return;
      }

      const storedDataKey = Object.keys(storedData)[0];

      // Remove item from stored data
      const index = storedData[storedDataKey].findIndex(
        (m) => m.id === this.item.id
      );
      storedData[storedDataKey].splice(index, 1);

      // Write data back to the cache
      store.writeQuery({ query: this.gqlQuery, data: storedData });
    },
    close(success) {
      this.$emit("input", false);
      if (success) {
        this.$emit("success");
      } else {
        this.$emit("cancel");
      }
    },
  },
  props: {
    value: {
      type: Boolean,
      required: true,
    },
    item: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    itemAttribute: {
      type: String,
      required: false,
      default: "name",
    },
    gqlMutation: {
      type: Object,
      required: true,
    },
    gqlQuery: {
      type: Object,
      required: false,
      default: null,
    },
  },
};
</script>
