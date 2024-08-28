<template>
  <BaseLayout>
    <v-container>
      <!-- Title and Description for better UX -->
      <v-row>
        <v-col>
          <h2>Log Generation Tool</h2>
          <p class="subtitle-1">
            Use this form to generate synthetic log data tailored to your
            application's needs. Fill out the fields below and click 'Generate
            Logs' to proceed.
          </p>
        </v-col>
      </v-row>

      <!-- Form for generating logs -->
      <v-form @submit.prevent="generateLogs">
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="formParams.app_type"
              :items="appTypes"
              label="Application Type"
              required
              hint="Select the type of application"
              persistent-hint
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="formParams.count"
              label="Number of logs"
              type="number"
              min="1"
              required
              hint="Specify the number of log entries to generate"
              persistent-hint
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="formParams.start_date"
              label="Start Date"
              type="date"
              required
              hint="Select the start date for log entries"
              persistent-hint
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="formParams.end_date"
              label="End Date"
              type="date"
              required
              hint="Select the end date for log entries"
              persistent-hint
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="formParams.ai_model_version_range"
              label="Model Version Range"
              placeholder="1.0.0-3.0.0"
              hint="Enter the range of model versions, e.g., 1.0.0-3.0.0"
              persistent-hint
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-btn color="primary" type="submit">Generate Logs</v-btn>
            <v-btn color="secondary" @click="downloadLogs">Download Logs</v-btn>
          </v-col>
        </v-row>
      </v-form>

      <!-- Displaying generated logs -->
      <v-row>
        <v-col cols="12" v-if="logs && logs.length">
          <h3>Generated Logs:</h3>
          <pre>{{ logs }}</pre>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import logGeneratorService from "@/services/logGeneratorService";
import BaseLayout from "@/components/BaseLayout.vue";
import { format } from "date-fns";

export default {
  name: "LogGenerator",
  components: {
    BaseLayout,
  },
  data() {
    return {
      appTypes: ["radiologist", "smart_cities", "smart_energy"],
      formParams: {
        app_type: "radiologist",
        count: 1,
        start_date: "2024-02-10",
        end_date: "2024-08-10",
        ai_model_version_range: "1.0.0-3.0.0",
      },
      logs: [],
    };
  },
  methods: {
    async generateLogs() {
      try {
        const formattedStartDate = format(
          new Date(this.formParams.start_date),
          "yyyy-MM-dd'T'HH:mm:ss'Z'"
        );
        const formattedEndDate = format(
          new Date(this.formParams.end_date),
          "yyyy-MM-dd'T'HH:mm:ss'Z'"
        );

        const params = {
          app_type: this.formParams.app_type,
          count: this.formParams.count,
          start_date: formattedStartDate,
          end_date: formattedEndDate,
          ai_model_version_range: this.formParams.ai_model_version_range,
        };

        const response = await logGeneratorService.generateLogs(params);
        this.downloadLogs(response.data);
      } catch (error) {
        console.error(
          "Error generating logs:",
          error.response?.data || error.message
        );
      }
    },
    downloadLogs() {
      logGeneratorService.downloadLogs();
    },
  },
};
</script>

<style scoped>
.subtitle-1 {
  margin-top: -5px;
  color: #757575;
}
</style>
