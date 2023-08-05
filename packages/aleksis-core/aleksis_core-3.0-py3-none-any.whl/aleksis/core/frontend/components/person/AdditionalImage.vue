<template>
  <v-dialog v-model="popup" max-width="fit-content" v-if="src">
    <template #activator="{ on, attrs }">
      <v-card v-bind="attrs" v-on="on">
        <v-img
          :src="src"
          :alt="$t('person.additional_image')"
          class="white--text align-end"
          gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
        >
          <v-card-title>{{ $t("person.additional_image") }}</v-card-title>
        </v-img>
      </v-card>
    </template>
    <v-sheet
      class="d-flex justify-center align-center flex-column text-center transparent"
    >
      <v-img
        :src="src"
        :alt="$t('person.additional_image')"
        width="80vmin"
        max-height="80vmin"
      />
    </v-sheet>
  </v-dialog>
  <v-card v-else>
    <v-list>
      <v-list-item>
        <v-list-item-icon>
          <v-icon>mdi-image-off-outline</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>
            {{ $t("person.no_additional_image") }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<script>
export default {
  name: "AdditionalImage",
  props: {
    src: {
      required: true,
      validator: (p) => {
        return typeof p === "string" || p === null;
      },
    },
  },
  data: () => ({
    popup: false,
  }),
};
</script>

<style scoped></style>
