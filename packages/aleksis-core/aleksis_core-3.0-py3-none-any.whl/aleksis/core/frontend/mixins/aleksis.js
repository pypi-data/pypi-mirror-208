/**
 * Mixin with utilities for AlekSIS view components.
 */
const aleksisMixin = {
  data: () => {
    return {
      $_aleksis_safeTrackedEvents: new Array(),
    };
  },
  methods: {
    safeAddEventListener(target, event, handler) {
      console.debug("Safely adding handler for %s on %o", event, target);
      target.addEventListener(event, handler);
      // Add to tracker so we can unregister the handler later
      this.$data.$_aleksis_safeTrackedEvents.push({
        target: target,
        event: event,
        handler: handler,
      });
    },
  },
  mounted() {
    this.$emit("mounted");
  },
  beforeDestroy() {
    // Unregister all safely added event listeners as to not leak them
    for (let trackedEvent in this.$data.$_aleksis_safeTrackedEvents) {
      if (trackedEvent.target) {
        console.debug(
          "Removing handler for %s on %o",
          trackedEvent.event,
          trackedEvent.target
        );
        trackedEvent.target.removeEventListener(
          trackedEvent.event,
          trackedEvent.handler
        );
      } else {
        console.debug("Target already removed while removing event handler");
      }
    }
  },
};

export default aleksisMixin;
