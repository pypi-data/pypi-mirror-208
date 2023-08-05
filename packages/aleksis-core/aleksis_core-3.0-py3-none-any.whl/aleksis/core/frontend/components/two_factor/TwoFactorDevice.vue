<template>
  <two-factor-device-base :icon="icon">
    <template #title>{{ device.methodVerboseName }}</template>
    <template #subtitles>
      <v-list-item-subtitle>
        {{ $t("accounts.two_factor.methods." + device.methodCode) }}
      </v-list-item-subtitle>
      <v-list-item-subtitle
        v-if="device.methodCode === 'call' || device.methodCode === 'sms'"
        class="black--text"
      >
        {{ device.verboseName }}
        <v-icon class="ml-1" color="green" small v-if="device.confirmed">
          mdi-check-circle-outline
        </v-icon>
      </v-list-item-subtitle>
    </template>
    <template #action>
      <!--      <v-btn icon color="red" v-if="!primary">-->
      <!--        <v-icon>mdi-delete</v-icon>-->
      <!--      </v-btn>-->
    </template>
  </two-factor-device-base>
</template>

<script>
import TwoFactorDeviceBase from "./TwoFactorDeviceBase.vue";

const iconMap = {
  sms: "mdi-message-text-outline",
  call: "mdi-phone-outline",
  webauthn: "mdi-key-outline",
  email: "mdi-email-outline",
  yubikey: "mdi-key",
};
export default {
  name: "TwoFactorDevice",
  components: { TwoFactorDeviceBase },
  computed: {
    icon() {
      if (this.device && this.device.methodCode in iconMap) {
        return iconMap[this.device.methodCode];
      }
      return "mdi-two-factor-authentication";
    },
  },
  props: {
    device: {
      type: Object,
      required: true,
    },
    primary: {
      type: Boolean,
      default: false,
    },
  },
};
</script>
