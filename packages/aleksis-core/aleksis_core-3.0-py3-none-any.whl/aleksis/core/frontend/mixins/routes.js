import gqlDynamicRoutes from "../components/app/dynamicRoutes.graphql";

/**
 * Vue mixin containing code getting dynamically added routes from other apps.
 *
 * Only used by main App component, but factored out for readability.
 */
const routesMixin = {
  data() {
    return {
      dynamicRoutes: null,
    };
  },
  apollo: {
    dynamicRoutes: {
      query: gqlDynamicRoutes,
      pollInterval: 10000,
    },
  },
  watch: {
    dynamicRoutes: {
      handler(newDynamicRoutes) {
        for (const route of newDynamicRoutes) {
          if (route) {
            console.debug("Adding new dynamic route:", route.routeName);
            let routeEntry = {
              path: route.routePath,
              name: route.routeName,
              component: () => import("../components/LegacyBaseTemplate.vue"),
              props: {
                byTheGreatnessOfTheAlmightyAleksolotlISwearIAmWorthyOfUsingTheLegacyBaseTemplate: true,
              },
              meta: {
                inMenu: route.displaySidenavMenu,
                inAccountMenu: route.displayAccountMenu,
                icon: route.menuIcon,
                rawTitleString: route.menuTitle,
                menuPermission: route.menuPermission,
                permission: route.routePermission,
                newTab: route.menuNewTab,
                dynamic: true,
                hide: false,
              },
            };

            if (route.parentRouteName) {
              this.$router.addRoute(route.parentRouteName, routeEntry);
            } else {
              this.$router.addRoute(routeEntry);
            }
          }
        }

        for (const route of this.$router
          .getRoutes()
          .filter((r) => r.meta.dynamic && !r.meta.hide)) {
          if (
            !(newDynamicRoutes.map((r) => r.routeName).indexOf(route.name) > -1)
          ) {
            let hiddenRoute = { ...route, meta: { ...route.meta, hide: true } };
            this.$router.addRoute(hiddenRoute);
          }
        }

        this.getPermissionNames();
        this.buildMenus();
      },
      deep: true,
    },
  },
};

export default routesMixin;
