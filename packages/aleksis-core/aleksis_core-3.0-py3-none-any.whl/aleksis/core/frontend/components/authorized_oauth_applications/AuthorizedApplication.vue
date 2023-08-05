<template>
  <v-expansion-panel>
    <v-expansion-panel-header v-slot="{ open }">
      <div class="d-flex justify-start align-center">
        <v-avatar
          x-large
          v-if="accessToken.application.icon.absoluteUrl"
          class="mr-4"
        >
          <img
            :src="accessToken.application.icon.absoluteUrl"
            :alt="accessToken.application.name"
          />
        </v-avatar>
        <v-avatar x-large v-else class="mr-4" color="secondary">
          <v-icon color="white">mdi-apps</v-icon>
        </v-avatar>
        <div class="subtitle-1 font-weight-medium">
          {{ accessToken.application.name }}
        </div>
      </div>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <v-list dense class="pa-0">
        <v-list-item>
          <v-list-item-content class="body-2">
            {{
              $t("oauth.authorized_application.access_since", {
                date: $d(new Date(accessToken.created), "longNumeric"),
              })
            }}
            ·
            {{
              $t("oauth.authorized_application.valid_until", {
                date: $d(new Date(accessToken.expires), "longNumeric"),
              })
            }}
          </v-list-item-content>
          <v-list-item-action>
            <v-btn color="primary" @click="deleteItem(accessToken)">
              {{ $t("oauth.authorized_application.revoke") }}
            </v-btn>
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="accessToken.scopes && accessToken.scopes.length > 0">
          <div class="pr-4">
            <v-list-item-content class="body-2">
              {{ $t("oauth.authorized_application.has_access_to") }}
            </v-list-item-content>
          </div>
          <v-list dense class="pa-0 flex-grow-1">
            <div v-for="(scope, idx) in accessToken.scopes" :key="scope.name">
              <v-list-item>
                <v-list-item-content class="body-2">
                  {{ scope.description }}
                </v-list-item-content>
              </v-list-item>
              <v-divider v-if="idx < accessToken.scopes.length - 1" />
            </div>
          </v-list>
        </v-list-item>
      </v-list>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
export default {
  name: "AuthorizedApplication",
  props: {
    accessToken: {
      type: Object,
      required: true,
    },
  },
  methods: {
    deleteItem(item) {
      this.$emit("delete-item", item);
    },
  },
};
</script>
