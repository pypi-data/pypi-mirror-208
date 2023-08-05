import gqlPing from "../components/app/ping.graphql";

/**
 * Mixin for handling of offline state / background queries.
 *
 * This handles three scenarios:
 *   - The navigator reports that it is in offline mode
 *   - The global offline flag was set due to network errors from queries
 *   - The navigator reports the page to be invisible
 *
 * The main goal is to save bandwidth, energy and server load in error
 * conditions, or when the page is not in focus. This is achieved by a
 * fallback strategy, where all background queries are stopped in offline
 * state, and only a ping query is sent once the navigator reports itself
 * as online and the app gets into focus. Once this ping query is successful,
 * background activity is resumed.
 */
const offlineMixin = {
  data() {
    return {
      ping: null,
    };
  },
  mounted() {
    this.safeAddEventListener(window, "online", () => {
      console.info("Navigator changed status to online.");
      this.checkOfflineState();
    });
    this.safeAddEventListener(window, "offline", () => {
      console.info("Navigator changed status to offline.");
      this.checkOfflineState();
    });
    this.safeAddEventListener(document, "visibilitychange", () => {
      console.info("Visibility changed status to", document.visibilityState);
      this.checkOfflineState();
    });
  },
  methods: {
    checkOfflineState() {
      if (navigator.onLine && document.visibilityState === "visible") {
        console.info("Resuming background activity");
        this.$root.backgroundActive = true;
      } else {
        console.info("Pausing background activity");
        this.$root.backgroundActive = false;
      }
    },
  },
  apollo: {
    ping: {
      query: gqlPing,
      variables: () => {
        return {
          payload: Date.now().toString(),
        };
      },
      pollInterval: 1000,
      skip: (component) => {
        // We only want to run this query when background activity is on and we are reported offline
        return !(component.$root.backgroundActive && component.$root.offline);
      },
    },
  },
  watch: {
    ping() {
      console.info("Pong received, clearing offline state");
      this.$root.offline = false;
    },
  },
};

export default offlineMixin;
