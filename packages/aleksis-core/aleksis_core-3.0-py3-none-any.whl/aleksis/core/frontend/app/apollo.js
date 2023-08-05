/*
 * Configuration for Apollo provider, client, and caches.
 */

import { ApolloClient, HttpLink, from } from "@/apollo-boost";

import { RetryLink } from "@/apollo-link-retry";
import { persistCache, LocalStorageWrapper } from "@/apollo3-cache-persist";
import { InMemoryCache } from "@/apollo-cache-inmemory";

// Cache for GraphQL query results in memory and persistent across sessions
const cache = new InMemoryCache();
await persistCache({
  cache: cache,
  storage: new LocalStorageWrapper(window.localStorage),
});

/**
 * Construct the GraphQL endpoint URI.
 *
 * @returns The URI of the GraphQL endpoint on the AlekSIS server
 */
function getGraphqlURL() {
  const settings = JSON.parse(
    document.getElementById("frontend_settings").textContent
  );
  const base = settings.urls.base || window.location.origin;
  return new URL(settings.urls.graphql, base);
}

// Define Apollo links for handling query operations.
const links = [
  // Automatically retry failed queries
  new RetryLink(),
  // Finally, the HTTP link to the real backend (Django)
  new HttpLink({
    uri: getGraphqlURL(),
  }),
];

/** Upstream Apollo GraphQL client */
const apolloClient = new ApolloClient({
  cache,
  link: from(links),
});

const apolloOpts = {
  defaultClient: apolloClient,
  defaultOptions: {
    $query: {
      skip: function (vm, queryKey) {
        if (queryKey in vm.$_apollo.queries) {
          // We only want to run this query when background activity is on and we are not reported offline
          return !!(
            vm.$_apollo.queries[queryKey].options.pollInterval &&
            (!vm.$root.backgroundActive || vm.$root.offline)
          );
        }
        return false;
      },
      error: ({ graphQLErrors, networkError }, vm) => {
        if (graphQLErrors) {
          for (let err of graphQLErrors) {
            console.error(
              "GraphQL query error in query",
              err.path.join("."),
              ":",
              err.message
            );
          }
          // Add a snackbar on all errors returned by the GraphQL endpoint
          //  If App is offline, don't add snackbar since only the ping query is active
          if (!vm.$root.offline && !vm.$root.invalidation) {
            vm.$root.snackbarItems.push({
              id: crypto.randomUUID(),
              timeout: 5000,
              messageKey: "graphql.snackbar_error_message",
              color: "red",
            });
          }
        }
        if (networkError && !vm.$root.invalidation) {
          // Set app offline globally on network errors
          //  This will cause the offline logic to kick in, starting a ping check or
          //  similar recovery strategies depending on the app/navigator state
          console.error("Network error:", networkError);
          console.error(
            "Network error during GraphQL query, setting offline state"
          );
          vm.$root.offline = true;
        }
      },
      fetchPolicy: "cache-and-network",
    },
  },
};

export default apolloOpts;
