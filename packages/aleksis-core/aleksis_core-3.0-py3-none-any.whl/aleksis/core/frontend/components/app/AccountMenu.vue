<template>
  <v-menu offset-y>
    <template #activator="{ on, attrs }">
      <v-avatar v-bind="attrs" v-on="on">
        <img
          v-if="
            systemProperties.sitePreferences.accountPersonPreferPhoto &&
            whoAmI.person.photo &&
            whoAmI.person.photo.url
          "
          :src="whoAmI.person.photo.url"
          :alt="whoAmI.person.fullName"
          :title="whoAmI.person.fullName"
        />
        <img
          v-else-if="whoAmI.person.avatarUrl"
          :src="whoAmI.person.avatarUrl"
          :alt="whoAmI.person.fullName + '(' + $t('person.avatar') + ')'"
          :title="whoAmI.person.fullName + '(' + $t('person.avatar') + ')'"
        />
        <v-icon v-else>mdi-person</v-icon>
      </v-avatar>
    </template>
    <v-list>
      <v-subheader>
        {{
          $t(
            whoAmI && whoAmI.isImpersonate
              ? "person.impersonation.impersonating"
              : "person.logged_in_as"
          )
        }}
        {{ whoAmI.person.fullName ? whoAmI.person.fullName : whoAmI.username }}
      </v-subheader>
      <v-list-item
        v-if="whoAmI && whoAmI.isImpersonate"
        :to="{ name: 'impersonate.stop', query: { next: $route.path } }"
      >
        <v-list-item-icon>
          <v-icon> mdi-stop</v-icon>
        </v-list-item-icon>
        <v-list-item-title>
          {{ $t("person.impersonation.stop") }}
        </v-list-item-title>
      </v-list-item>
      <div v-for="menuItem in accountMenu" :key="menuItem.name">
        <v-divider v-if="menuItem.divider"></v-divider>
        <v-list-item
          :to="{ name: menuItem.name }"
          :target="menuItem.newTab ? '_blank' : '_self'"
        >
          <v-list-item-icon>
            <v-icon v-if="menuItem.icon">{{ menuItem.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{
            !menuItem.rawTitleString
              ? $t(menuItem.titleKey)
              : menuItemm.rawTitleString
          }}</v-list-item-title>
        </v-list-item>
      </div>
    </v-list>
  </v-menu>
</template>

<script>
export default {
  name: "AccountMenu",
  props: {
    accountMenu: {
      type: Array,
      required: false,
      default: () => [],
    },
    systemProperties: {
      type: Object,
      required: true,
    },
    whoAmI: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style></style>
