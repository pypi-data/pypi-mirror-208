<template>
  <div>
    <h1 class="mb-4">{{ $t("accounts.two_factor.title") }}</h1>
    <div v-if="$apollo.queries.twoFactor.loading">
      <v-skeleton-loader type="card,card"></v-skeleton-loader>
    </div>
    <div v-else-if="twoFactor && twoFactor.activated">
      <v-card class="mb-4">
        <v-card-title>
          {{ $t("accounts.two_factor.primary_device_title") }}
        </v-card-title>
        <v-card-text>
          {{ $t("accounts.two_factor.primary_device_description") }}
        </v-card-text>
        <v-list three-line>
          <two-factor-device :device="twoFactor.defaultDevice" primary />
        </v-list>
      </v-card>

      <v-card class="mb-4">
        <v-card-title>
          {{ $t("accounts.two_factor.other_devices_title") }}
        </v-card-title>
        <v-card-text>
          {{ $t("accounts.two_factor.other_devices_description") }}
        </v-card-text>
        <v-list three-line>
          <div v-for="(device, index) in twoFactor.otherDevices" :key="index">
            <two-factor-device :device="device" />
            <v-divider />
          </div>

          <two-factor-device-base icon="mdi-backup-restore">
            <template #title>
              {{ $t("accounts.two_factor.backup_codes_title") }}
            </template>
            <template #subtitles>
              <v-list-item-subtitle>
                {{ $t("accounts.two_factor.backup_codes_description") }}
              </v-list-item-subtitle>
              <v-list-item-subtitle>
                {{
                  $tc(
                    "accounts.two_factor.backup_codes_count",
                    twoFactor.backupTokensCount,
                    { counter: twoFactor.backupTokensCount }
                  )
                }}
              </v-list-item-subtitle>
            </template>
            <template #action>
              <v-btn icon :to="{ name: 'core.twoFactor.backupTokens' }">
                <v-icon>mdi-chevron-right</v-icon>
              </v-btn>
            </template>
          </two-factor-device-base>
        </v-list>
        <v-card-actions>
          <v-btn text color="primary" :to="{ name: 'core.twoFactor.add' }">
            <v-icon left>mdi-key-plus</v-icon>
            {{ $t("accounts.two_factor.add_authentication_method") }}
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card class="mb-4">
        <v-card-title>{{
          $t("accounts.two_factor.disable_title")
        }}</v-card-title>
        <v-card-text>
          {{ $t("accounts.two_factor.disable_description") }}
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="red"
            class="white--text"
            :to="{ name: 'core.twoFactor.disable' }"
          >
            <v-icon left>mdi-power</v-icon>
            {{ $t("accounts.two_factor.disable_button") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
    <div v-else>
      <v-card class="mb-4">
        <v-card-title>
          {{ $t("accounts.two_factor.enable_title") }}
        </v-card-title>
        <v-card-text>
          {{ $t("accounts.two_factor.enable_description") }}
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="green"
            class="white--text"
            :to="{ name: 'core.twoFactor.setup' }"
          >
            <v-icon left>mdi-power</v-icon>
            {{ $t("accounts.two_factor.enable_button") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script>
import gqlTwoFactor from "./twoFactor.graphql";
import TwoFactorDevice from "./TwoFactorDevice.vue";
import TwoFactorDeviceBase from "./TwoFactorDeviceBase.vue";

export default {
  name: "TwoFactor",
  components: { TwoFactorDeviceBase, TwoFactorDevice },
  apollo: {
    twoFactor: {
      query: gqlTwoFactor,
      fetchPolicy: "network-only",
    },
  },
};
</script>
