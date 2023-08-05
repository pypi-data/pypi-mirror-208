/**
 * Vue mixin to register the PWA service worker once the main
 * component gets ready.
 */
const useRegisterSWMixin = {
  name: "useRegisterSW",
  data() {
    return {
      updateSW: undefined,
      offlineReady: false,
      needRefresh: false,
      refreshDismissed: false,
    };
  },
  async mounted() {
    try {
      const { registerSW } = await import("virtual:pwa-register");
      const vm = this;
      this.updateSW = registerSW({
        onOfflineReady() {
          vm.offlineReady = true;
          console.log("PWA is offline-ready.");
        },
        onNeedRefresh() {
          vm.needRefresh = true;
          console.log("PWA needs to be refreshed.");
        },
        onRegisteredSW(swUrl, r) {
          r &&
            setInterval(async () => {
              if (!(!r.installing && navigator)) return;

              if ("connection" in navigator && !navigator.onLine) return;

              const resp = await fetch(swUrl, {
                cache: "no-store",
                headers: {
                  cache: "no-store",
                  "cache-control": "no-cache",
                },
              });

              if (resp?.status === 200) await r.update();
            }, 60 * 60 * 1000);
        },
        onRegisterError(e) {
          console.log("Error while installing PWA: " + e);
        },
      });
    } catch {
      console.log("PWA disabled.");
    }
  },
  methods: {
    updateServiceWorker() {
      this.offlineReady = false;
      this.needRefresh = false;
      this.updateSW && this.updateSW(true);
    },
  },
};

export default useRegisterSWMixin;
