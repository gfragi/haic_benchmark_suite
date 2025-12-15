<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col cols="12" md="6">
          <h2>Logs for Configuration</h2>
        </v-col>
        <v-col cols="12" md="6" class="text-right">
          <v-autocomplete
            v-model="selectedConfig"
            :items="configurations"
            item-title="application_name"
            item-value="id"
            label="Select Configuration"
            @change="onConfigChange"
            solo
            hide-details
          ></v-autocomplete>
        </v-col>
      </v-row>

      <v-data-table
        :headers="headers"
        :items="filteredLogs"
        class="elevation-1"
        :loading="loading"
        loading-text="Loading logs..."
        v-if="selectedConfig"
      >
        <template v-slot:[`item.actions`]="{ item }">
          <v-btn icon @click="downloadLog(item)">
            <v-icon>mdi-download</v-icon>
          </v-btn>
          <v-btn icon color="red" @click="deleteLog(item)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>

      <v-row justify="end" class="mt-4" v-if="selectedConfig">
        <v-btn
          color="primary"
          @click="downloadAllLogs"
          :disabled="logs.length === 0"
        >
          Download All Logs
        </v-btn>
      </v-row>

      <v-snackbar v-model="snackbar" :timeout="5000">
        {{ snackbarText }}
        <v-btn color="pink" text @click="snackbar = false">Close</v-btn>
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script>
import logService from "@/services/logService";
import configurationService from "@/services/configurationService";
import BaseLayout from "@/components/BaseLayout";
// import { map } from "lodash";

export default {
  name: "LogManagement",
  components: {
    BaseLayout,
  },
  data() {
    return {
      selectedConfig: null,
      configurations: [],
      logs: [],
      search: "",
      loading: false,
      snackbar: false,
      snackbarText: "",
      headers: [
        { text: "Log File Name", value: "log_name" },
        { text: "Type", value: "folder" },
        { text: "Actions", value: "actions", sortable: false, align: "center" },
      ],
    };
  },
  watch: {
    selectedConfig(newVal) {
      console.log("Configuration selected:", newVal);
      this.onConfigChange();
    },
  },
  computed: {
    filteredLogs() {
      return this.logs.filter((log) =>
        log.log_name.toLowerCase().includes(this.search.toLowerCase())
      );
    },
  },
  mounted() {
    this.fetchConfigurations();
  },
  methods: {
    fetchConfigurations() {
      configurationService
        .getAllConfigs()
        .then((response) => {
          this.configurations = response.data;
        })
        .catch((error) => {
          this.showSnackbar("Error fetching configurations.");
          console.error("Error fetching configurations:", error);
        });
    },
    onConfigChange() {
      if (this.selectedConfig) {
        this.fetchLogs();
      }
    },
    fetchLogs() {
      if (!this.selectedConfig) {
        this.showSnackbar("Please select a configuration.");
        return;
      }

      this.loading = true;
      logService
        .getLogs(this.selectedConfig)
        .then((response) => {
          this.logs = response.data.logs.map((key) => {
            const parts = key.split("/");
            return {
              object_key: key,
              log_name: parts[parts.length - 1],
              folder: parts[1] ? parts[1].toUpperCase() : "UNKNOWN",
            };
          });
        })
        .catch((error) => {
          this.showSnackbar("Error fetching logs.");
          console.error("Error fetching logs:", error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    downloadLog(log) {
      logService
        .downloadLog(this.selectedConfig, log.object_key)
        .then((response) => {
          window.open(response.data.download_url, "_blank");
        })
        .catch((error) => {
          this.showSnackbar("Error downloading log.");
          console.error("Error downloading log:", error);
        });
    },
    deleteLog(log) {
      if (
        confirm(`Are you sure you want to delete the log ${log.object_key}?`)
      ) {
        logService
          .deleteLog(this.selectedConfig, log.object_key)
          .then(() => {
            this.showSnackbar("Log deleted successfully.");
            this.fetchLogs(); // Refresh the log list after deletion
          })
          .catch((error) => {
            this.showSnackbar("Error deleting log.");
            console.error("Error deleting log:", error);
          });
      }
    },
    downloadAllLogs() {
      if (!confirm("Are you sure you want to download all logs?")) return;

      this.logs.forEach((log) => {
        this.downloadLog(log);
      });
    },
    showSnackbar(message) {
      this.snackbarText = message;
      this.snackbar = true;
    },
  },
};
</script>
