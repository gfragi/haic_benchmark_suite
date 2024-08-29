<template>
  <BaseLayout>
    <v-container>
      <h2>Logs for Configuration ID: {{ configId }}</h2>
      <v-data-table :headers="headers" :items="logs" class="elevation-1">
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn color="primary" @click="downloadLog(item)"> Download </v-btn>
          <v-btn color="error" @click="deleteLog(item)"> Delete </v-btn>
        </template>
      </v-data-table>
    </v-container>
  </BaseLayout>
</template>

<script>
import logService from "@/services/logService";
import BaseLayout from "@/components/BaseLayout";

export default {
  name: "LogManagement",
  components: {
    BaseLayout,
  },
  data() {
    return {
      configId: this.$route.params.configId, // Assuming configId is passed as a route parameter
      logs: [],
      headers: [
        { title: "Log File Name", key: "log_name" },
        { title: "Actions", key: "actions", sortable: false },
      ],
    };
  },
  mounted() {
    this.fetchLogs();
  },
  methods: {
    fetchLogs() {
      logService
        .getLogsByConfigId(this.configId)
        .then((response) => {
          this.logs = response.data.logs.map((log) => ({ log_name: log }));
        })
        .catch((error) => {
          console.error("Error fetching logs:", error);
        });
    },
    downloadLog(log) {
      // Call backend to get the pre-signed URL for download
      logService
        .downloadLog(this.configId, log.log_name)
        .then((response) => {
          window.open(response.data.download_url, "_blank");
        })
        .catch((error) => {
          console.error("Error downloading log:", error);
        });
    },
    deleteLog(log) {
      if (confirm(`Are you sure you want to delete the log ${log.log_name}?`)) {
        logService
          .deleteLog(this.configId, log.log_name)
          .then(() => {
            this.fetchLogs(); // Refresh the log list after deletion
          })
          .catch((error) => {
            console.error("Error deleting log:", error);
          });
      }
    },
  },
};
</script>
