<template>
  <v-menu
    offset-y
    :close-on-content-click="false"
    max-width="min(600px, 80vw)"
    width="min-content"
    max-height="90%"
  >
    <template #activator="{ on, attrs }">
      <v-btn
        icon
        color="primary"
        v-bind="attrs"
        v-on="on"
        :loading="$apollo.queries.myNotifications.loading"
        class="mx-2"
      >
        <v-icon
          color="white"
          v-if="
            myNotifications &&
            myNotifications.person &&
            myNotifications.person.unreadNotificationsCount > 0
          "
        >
          mdi-bell-badge-outline
        </v-icon>
        <v-icon color="white" v-else>mdi-bell-outline</v-icon>
      </v-btn>
    </template>
    <v-skeleton-loader
      v-if="$apollo.queries.myNotifications.loading"
      class="mx-auto"
      type="paragraph"
    ></v-skeleton-loader>
    <v-list v-else nav three-line dense class="overflow-y-auto">
      <template
        v-if="
          myNotifications.person &&
          myNotifications.person.notifications &&
          myNotifications.person.notifications.length
        "
      >
        <v-subheader>{{ $t("notifications.notifications") }}</v-subheader>
        <template v-for="notification in myNotifications.person.notifications">
          <NotificationItem
            :key="notification.id"
            :notification="notification"
          />
          <v-divider
            v-if="
              notification !==
              myNotifications.person.notifications[
                myNotifications.person.notifications.length - 1
              ]
            "
            :key="notification.id + '-divider'"
          ></v-divider>
        </template>
      </template>
      <template v-else>
        <v-list-item>
          <div class="d-flex justify-center align-center flex-column">
            <div class="mb-4">
              <v-icon large color="primary">mdi-bell-off-outline</v-icon>
            </div>
            <div>{{ $t("notifications.no_notifications") }}</div>
          </div>
        </v-list-item>
      </template>
    </v-list>
  </v-menu>
</template>

<script>
import NotificationItem from "./NotificationItem.vue";
import gqlMyNotifications from "./myNotifications.graphql";

export default {
  components: {
    NotificationItem,
  },
  apollo: {
    myNotifications: {
      query: gqlMyNotifications,
      pollInterval: 1000,
    },
  },
};
</script>
