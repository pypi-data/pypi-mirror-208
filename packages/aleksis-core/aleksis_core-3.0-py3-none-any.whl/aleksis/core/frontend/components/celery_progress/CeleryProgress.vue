<!-- Display the progress/status of a background task on the server -->

<template>
  <small-container>
    <v-card :loading="$apollo.loading">
      <v-card-title v-if="progress">
        {{ progress.meta.title }}
      </v-card-title>
      <v-card-text v-if="progress">
        <v-progress-linear
          :value="progress.progress.percent"
          buffer-value="0"
          color="primary"
          class="mb-2"
          stream
        />
        <div class="text-center mb-4">
          {{
            progress.meta.progressTitle
              ? progress.meta.progressTitle
              : $t("celery_progress.progress_title")
          }}
        </div>
        <div v-if="progress">
          <message-box
            v-for="(message, idx) in progress.messages"
            dense
            :type="message.tag"
            transition="slide-x-transition"
            :key="idx"
          >
            {{ message.message }}
          </message-box>
        </div>
        <message-box
          v-if="progress.state === 'FAILURE'"
          dense
          type="error"
          transition="slide-x-transition"
        >
          {{
            progress.meta.errorMessage
              ? progress.meta.errorMessage
              : $t("celery_progress.error_message")
          }}
        </message-box>
        <message-box
          v-if="progress.state === 'SUCCESS'"
          dense
          type="success"
          transition="slide-x-transition"
        >
          {{
            progress.meta.successMessage
              ? progress.meta.successMessage
              : $t("celery_progress.success_message")
          }}
        </message-box>
      </v-card-text>
      <v-card-actions
        v-if="
          progress &&
          (progress.state === 'FAILURE' || progress.state === 'SUCCESS')
        "
      >
        <back-button :href="progress.meta.backUrl" text />
        <v-spacer />
        <v-btn
          v-if="progress.meta.additionalButton && progress.state === 'SUCCESS'"
          :href="progress.meta.additionalButton.url"
          text
          color="primary"
        >
          <v-icon v-if="progress.meta.additionalButton.icon" left>
            {{ progress.meta.additionalButton.icon }}
          </v-icon>
          {{ progress.meta.additionalButton.title }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </small-container>
</template>

<script>
import gqlCeleryProgress from "./celeryProgress.graphql";
import gqlCeleryProgressFetched from "./celeryProgressFetched.graphql";

export default {
  name: "CeleryProgress",
  apollo: {
    celeryProgressByTaskId: {
      query: gqlCeleryProgress,
      variables() {
        return {
          taskId: this.$route.params.taskId,
        };
      },
      pollInterval: 1000,
    },
  },
  computed: {
    progress() {
      return this.celeryProgressByTaskId;
    },
    state() {
      return this.progress ? this.progress.state : null;
    },
  },
  watch: {
    state(newState) {
      if (newState === "SUCCESS" || newState === "FAILURE") {
        this.$apollo.queries.celeryProgressByTaskId.stopPolling();
        this.$apollo.mutate({
          mutation: gqlCeleryProgressFetched,
          variables: {
            taskId: this.$route.params.taskId,
          },
        });
      }
      if (newState === "SUCCESS" && this.progress.meta.redirectOnSuccessUrl) {
        this.$router.push(this.progress.meta.redirectOnSuccessUrl);
      }
    },
  },
};
</script>
