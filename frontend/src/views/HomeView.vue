<template>
  <BaseLayout>
    <v-container class="ml-auto">
      <h1 class="text-center my-4">Welcome to the HAIC Evaluation Platform</h1>
      <v-row>
        <v-col cols="12" md="4">
          <v-card elevation="2">
            <v-card-title>
              <v-icon left class="mr-2">mdi-cog</v-icon>
              Manage Configurations
            </v-card-title>
            <v-card-text>
              Create and manage your evaluation configurations.
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/configs">Go to Configurations</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card elevation="2">
            <v-card-title>
              <v-icon left class="mr-2">mdi-file-upload</v-icon>
              Ingest Logs
            </v-card-title>
            <v-card-text> Upload and manage your log data. </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/logs">Go to Log Ingestion</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card elevation="2">
            <v-card-title>
              <v-icon left class="mr-2">mdi-chart-line</v-icon>
              View Results
            </v-card-title>
            <v-card-text> Analyze your evaluation results. </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/results">Go to Results</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="4">
          <v-card elevation="2">
            <v-card-title>
              <v-icon left class="mr-2">mdi-file-document</v-icon>
              Generate Reports
            </v-card-title>
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

<style scoped>
.text-center {
  text-align: center;
}

.my-4 {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.mr-2 {
  margin-right: 0.5rem;
}
</style>
