<template>
  <v-navigation-drawer app :value="value" @input="$emit('input', $event)">
    <v-list nav dense shaped>
      <v-list-item class="logo">
        <a
          id="logo-container"
          @click="$router.push({ name: 'dashboard' })"
          class="brand-logo"
        >
          <brand-logo :site-preferences="systemProperties.sitePreferences" />
        </a>
      </v-list-item>
      <v-list-item class="search">
        <sidenav-search />
      </v-list-item>
      <v-list-item-group :value="$route.name" v-if="sideNavMenu">
        <div v-for="menuItem in sideNavMenu" :key="menuItem.name">
          <v-list-group
            v-if="menuItem.subMenu.length > 0"
            href="#!"
            :prepend-icon="menuItem.icon"
            :value="
              $route.matched.slice(-2).shift()
                ? $route.matched.slice(-2).shift().name === menuItem.name
                : false
            "
          >
            <template #activator>
              <v-list-item-title
                >{{
                  !menuItem.rawTitleString
                    ? $t(menuItem.titleKey)
                    : menuItem.rawTitleString
                }}
              </v-list-item-title>
            </template>
            <v-list-item
              v-for="subMenuItem in menuItem.subMenu"
              exact
              :to="{ name: subMenuItem.name }"
              :target="subMenuItem.newTab ? '_blank' : '_self'"
              :key="subMenuItem.name"
              :value="subMenuItem.name"
            >
              <v-list-item-icon>
                <v-icon v-if="subMenuItem.icon">{{ subMenuItem.icon }} </v-icon>
              </v-list-item-icon>
              <v-list-item-title
                >{{
                  !subMenuItem.rawTitleString
                    ? $t(subMenuItem.titleKey)
                    : subMenuItem.rawTitleString
                }}
              </v-list-item-title>
            </v-list-item>
          </v-list-group>
          <v-list-item
            v-else
            exact
            :to="{ name: menuItem.name }"
            :target="menuItem.newTab ? '_blank' : '_self'"
            :value="menuItem.name"
          >
            <v-list-item-icon>
              <v-icon v-if="menuItem.icon">{{ menuItem.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{
              !menuItem.rawTitleString
                ? $t(menuItem.titleKey)
                : menuItem.rawTitleString
            }}</v-list-item-title>
          </v-list-item>
        </div>
      </v-list-item-group>
      <template v-else>
        <v-skeleton-loader class="ma-2" type="list-item@5" />
      </template>
    </v-list>

    <template #append>
      <div class="pa-4 d-flex justify-center align-center">
        <v-spacer />
        <language-form
          :available-languages="systemProperties.availableLanguages"
        />
        <v-spacer />
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script>
import BrandLogo from "./BrandLogo.vue";
import LanguageForm from "./LanguageForm.vue";
import SidenavSearch from "./SidenavSearch.vue";

export default {
  name: "SideNav",
  components: {
    BrandLogo,
    LanguageForm,
    SidenavSearch,
  },
  props: {
    sideNavMenu: { type: Array, required: false, default: null },
    systemProperties: { type: Object, required: true },
    value: { type: Boolean, required: true },
  },
};
</script>

<style scoped></style>
