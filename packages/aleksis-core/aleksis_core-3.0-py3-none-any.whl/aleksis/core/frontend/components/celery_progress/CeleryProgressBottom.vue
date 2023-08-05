<template>
  <v-bottom-sheet :value="show" persistent hide-overlay max-width="400px">
    <v-expansion-panels accordion v-model="open">
      <v-expansion-panel>
        <v-expansion-panel-header color="primary" class="white--text px-4">
          {{
            $tc("celery_progress.running_tasks", numberOfTasks, {
              number: numberOfTasks,
            })
          }}
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <div class="mx-n6 mb-n4" v-if="celeryProgressByUser">
            <task-list-item
              v-for="task in celeryProgressByUser"
              :task="task"
              :key="task.meta.taskId"
            />
          </div>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-bottom-sheet>
</template>

<script>
import TaskListItem from "./TaskListItem.vue";
import gqlCeleryProgressButton from "./celeryProgressBottom.graphql";

export default {
  name: "CeleryProgressBottom",
  components: { TaskListItem },
  data() {
    return { open: 0 };
  },
  computed: {
    show() {
      return this.celeryProgressByUser && this.celeryProgressByUser.length > 0;
    },
    numberOfTasks() {
      if (!this.celeryProgressByUser) {
        return 0;
      }
      return this.celeryProgressByUser.length;
    },
  },
  apollo: {
    celeryProgressByUser: {
      query: gqlCeleryProgressButton,
      pollInterval: 1000,
    },
  },
};
</script>
