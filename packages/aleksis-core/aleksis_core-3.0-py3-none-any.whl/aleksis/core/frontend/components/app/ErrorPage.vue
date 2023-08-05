<template>
  <div
    class="d-flex justify-center align-center flex-column text-center"
    id="wrapper"
  >
    <h1 class="text-h2">{{ $t(shortErrorMessageKey) }}</h1>
    <div>{{ $t(longErrorMessageKey) }}</div>
    <v-btn
      color="secondary"
      :to="{ name: redirectRouteName }"
      v-if="!hideButton"
    >
      <v-icon left>{{ redirectButtonIcon }}</v-icon>
      {{ $t(redirectButtonTextKey) }}
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "ErrorPage",
  props: {
    shortErrorMessageKey: {
      type: String,
      required: true,
    },
    longErrorMessageKey: {
      type: String,
      required: true,
    },
    redirectButtonTextKey: {
      type: String,
      required: true,
    },
    redirectRouteName: {
      type: String,
      required: true,
    },
    redirectButtonIcon: {
      type: String,
      required: true,
    },
    hideButton: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
};
</script>

<style scoped>
#wrapper {
  min-height: 70vh;
  gap: 1em;
}
</style>
