<template>
  <v-list-item
    :key="task.meta.taskId"
    :to="{ name: 'core.celery_progress', params: { taskId: task.meta.taskId } }"
  >
    <v-list-item-content>
      <v-list-item-title>{{ task.meta.title }}</v-list-item-title>
      <v-list-item-subtitle>{{ task.meta.progressTitle }}</v-list-item-subtitle>
    </v-list-item-content>

    <v-list-item-action>
      <v-progress-circular
        v-if="!task.complete"
        color="primary"
        :value="task.progress.percent"
      />
      <v-icon size="32px" v-else-if="task.state === 'SUCCESS'" color="success"
        >mdi-check-circle-outline</v-icon
      >
      <v-icon size="32px" v-else color="error">mdi-alert-circle-outline</v-icon>
    </v-list-item-action>
  </v-list-item>
</template>

<script>
export default {
  name: "TaskListItem",
  props: {
    task: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped></style>
