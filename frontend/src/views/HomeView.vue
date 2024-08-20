<template>
  <BaseLayout>
    <v-container>
      <h1>Welcome to the HAIC Evaluation Platform</h1>
      <v-row>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Manage Configurations</v-card-title>
            <v-card-text>
              Create and manage your evaluation configurations.
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/configs">Go to Configurations</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Ingest Logs</v-card-title>
            <v-card-text> Upload and manage your log data. </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/logs">Go to Log Ingestion</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>View Results</v-card-title>
            <v-card-text> Analyze your evaluation results. </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/results">Go to Results</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Generate Reports</v-card-title>
            <v-card-text> Create and download evaluation reports. </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/reports">Go to Reports</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  components: {
    BaseLayout,
  },
  name: "HomeView",
};
</script>
