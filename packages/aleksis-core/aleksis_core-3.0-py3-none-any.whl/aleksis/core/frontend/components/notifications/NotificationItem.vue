<template>
  <ApolloMutation
    :mutation="require('./markNotificationRead.graphql')"
    :variables="{ id: this.notification.id }"
  >
    <template #default="{ mutate, loading, error }">
      <v-list-item :input-value="!notification.read">
        <v-list-item-avatar>
          <v-icon
            :class="
              notification.read ? 'grey lighten-1' : 'primary white--text'
            "
            dark
          >
            mdi-{{ notification.icon.toLowerCase().replaceAll("_", "-") }}
          </v-icon>
        </v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>
            {{ notification.title }}
          </v-list-item-title>

          <v-list-item-subtitle class="font-weight-regular">
            {{ notification.description }}
          </v-list-item-subtitle>

          <v-list-item-subtitle class="caption font-weight-regular">
            <v-chip x-small outlined>{{ notification.sender }}</v-chip>
            ·
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">{{
                  $d(
                    new Date(notification.created),
                    dateFormat(new Date(notification.created))
                  )
                }}</span>
              </template>
              <span>{{ $d(new Date(notification.created), "long") }}</span>
            </v-tooltip>
          </v-list-item-subtitle>
        </v-list-item-content>

        <v-list-item-action>
          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                icon
                color="secondary"
                v-if="!notification.read"
                @click="mutate"
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>mdi-email-outline</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("notifications.mark_as_read") }}</span>
          </v-tooltip>

          <v-tooltip bottom>
            <template #activator="{ on, attrs }">
              <v-btn
                icon
                color="accent"
                :href="notification.link"
                v-if="notification.link"
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>mdi-open-in-new</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("notifications.more_information") }}</span>
          </v-tooltip>
        </v-list-item-action>
      </v-list-item>
    </template>
  </ApolloMutation>
</template>

<script>
export default {
  props: {
    notification: {
      type: Object,
      required: true,
    },
  },
  methods: {
    dateFormat(date) {
      let now = new Date();
      if (
        now.getFullYear() === date.getFullYear() &&
        now.getMonth() === date.getMonth() &&
        now.getDate() === date.getDate()
      ) {
        return "timeOnly";
      } else {
        return "short";
      }
    },
  },
};
</script>
