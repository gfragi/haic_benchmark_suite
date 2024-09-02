<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Results for Configuration ID: {{ configId }}</h2>

      <!-- List of Runs -->
      <v-row>
        <v-col cols="12" md="4">
          <v-autocomplete
            v-model="selectedRun"
            :items="runDates"
            item-title="text"
            item-value="value"
            label="Select Evaluation Run"
            @change="fetchRunMetrics"
            solo
            hide-details
          ></v-autocomplete>
        </v-col>
      </v-row>

      <!-- Display Metrics Grouped -->
      <v-row v-if="selectedRun && groupedMetrics">
        <v-col
          cols="12"
          v-for="(metrics, groupName) in groupedMetrics"
          :key="groupName"
        >
          <v-card>
            <v-card-title>{{ groupName }}</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="metricHeaders"
                :items="metrics"
                class="elevation-1"
              >
                <template v-slot:[`item.metric`]="{ item }">
                  {{ item.metric }}
                </template>
                <template v-slot:[`item.value`]="{ item }">
                  {{ item.value }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-else>
        <v-col cols="12">
          <p>Please select a run to view metrics.</p>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationService from "@/services/resultService";

export default {
  components: {
    BaseLayout,
  },
  data() {
    return {
      configId: null,
      runDates: [],
      selectedRun: null,
      groupedMetrics: null,
      metricHeaders: [
        { text: "Metric", value: "metric" },
        { text: "Value", value: "value" },
      ],
    };
  },
  mounted() {
    this.configId = this.$route.params.configId; // Ensure configId is set from the route params
    console.log("Config ID:", this.configId); // Debugging line
    this.fetchRunDates();
  },
  watch: {
    selectedRun(newRunId) {
      if (newRunId) {
        console.log("Watcher triggered for selectedRun: ", newRunId);
        this.fetchRunMetrics(newRunId);
      }
    },
  },
  methods: {
    fetchRunDates() {
      if (!this.configId) {
        console.error("Config ID is undefined.");
        return;
      }
      evaluationService
        .getEvaluationResultsByConfig(this.configId)
        .then((response) => {
          console.log("Fetched Run Dates: ", response.data); // Log the response data
          // Extract the evaluation dates for selection
          this.runDates = response.data.map((run) => ({
            text: `Run on ${new Date(run.evaluation_date).toLocaleString()}`,
            value: run.id,
          }));
          console.log("Mapped Run Dates: ", this.runDates); // Log the mapped run dates
        })
        .catch((error) => {
          console.error("Error fetching evaluation run dates:", error);
        });
    },
    fetchRunMetrics(runId) {
      if (runId) {
        console.log("Fetching metrics for run ID: ", runId); // Log selected run ID
        evaluationService
          .getEvaluationResultDetail(this.configId, runId) // Pass both configId and runId
          .then((response) => {
            console.log("Fetched Run Metrics: ", response.data); // Log fetched metrics data
            this.groupedMetrics = this.groupMetricsByCategory(response.data);
          })
          .catch((error) => {
            console.error("Error fetching evaluation run metrics:", error);
          });
      }
    },
    groupMetricsByCategory(result) {
      const groupedMetrics = {
        Performance: [],
        Efficiency: [],
        "Adaptability and Learning": [],
        "Collaboration and Interaction": [],
        "Trust and Safety": [],
        "Robustness and Generalization": [],
      };

      console.log("Raw Metrics Data: ", result); // Log raw result data
      const excludedKeys = ["id", "configuration_id", "evaluation_date"];
      const metrics = Object.keys(result)
        .filter((key) => !excludedKeys.includes(key))
        .map((key) => ({
          metric: key.replace(/_/g, " ").toUpperCase(),
          value: result[key],
        }));

      metrics.forEach((metric) => {
        console.log("Processing Metric: ", metric); // Log each metric being processed
        if (
          groupedMetrics["Performance"].some(
            (item) => item.metric === metric.metric
          )
        ) {
          groupedMetrics["Performance"].push(metric);
        } else if (
          groupedMetrics["Efficiency"].some(
            (item) => item.metric === metric.metric
          )
        ) {
          groupedMetrics["Efficiency"].push(metric);
        } else if (
          groupedMetrics["Adaptability and Learning"].some(
            (item) => item.metric === metric.metric
          )
        ) {
          groupedMetrics["Adaptability and Learning"].push(metric);
        } else if (
          groupedMetrics["Collaboration and Interaction"].some(
            (item) => item.metric === metric.metric
          )
        ) {
          groupedMetrics["Collaboration and Interaction"].push(metric);
        } else if (
          groupedMetrics["Trust and Safety"].some(
            (item) => item.metric === metric.metric
          )
        ) {
          groupedMetrics["Trust and Safety"].push(metric);
        } else if (
          groupedMetrics["Robustness and Generalization"].some(
            (item) => item.metric === metric.metric
          )
        ) {
          groupedMetrics["Robustness and Generalization"].push(metric);
        }
      });

      console.log("Grouped Metrics: ", groupedMetrics); // Log the final grouped metrics
      return groupedMetrics;
    },
  },
};
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
}
.v-list-item-title {
  font-weight: bold;
}
</style>
