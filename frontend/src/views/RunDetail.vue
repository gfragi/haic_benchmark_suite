<template>
  <BaseLayout>
    <v-container>
      <!-- Run Information Title -->
      <v-row>
        <v-col>
          <v-card class="pa-3 mb-4">
            <v-card-title class="headline">
              Run Details: Configuration ID {{ configId }}, Run ID {{ runId
              }}<br />
              Application: {{ applicationName }}
            </v-card-title>
            <v-card-subtitle>
              This page displays metrics for the selected run. You can explore
              the metric groups on the left to see the performance, efficiency,
              and more.
            </v-card-subtitle>
          </v-card>
        </v-col>
      </v-row>

      <v-row>
        <!-- Left Sidebar for Metric Groups -->
        <v-col cols="3">
          <v-list dense>
            <v-list-item
              v-for="(metrics, groupName) in groupedMetrics"
              :key="groupName"
              @click="selectGroup(groupName)"
              :class="{ 'selected-group': selectedGroup === groupName }"
              style="cursor: pointer"
            >
              <v-list-item-icon>
                <v-icon>{{ getGroupIcon(groupName) }}</v-icon>
                <!-- Group Icon -->
              </v-list-item-icon>
              <v-list-item-title>{{ groupName }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-col>
        <!-- Main Content Area for Metrics -->
        <v-col cols="6">
          <v-card v-if="selectedGroup">
            <v-card-title>{{ selectedGroup }} Metrics</v-card-title>
            <v-card-text>
              <v-list dense>
                <v-list-item
                  v-for="(metric, index) in groupedMetrics[selectedGroup]"
                  :key="index"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ metric.metric }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <strong>Value:</strong> {{ metric.value }}
                    </v-list-item-subtitle>
                    <!-- Add a brief explanation for each metric -->
                    <p class="metric-description">
                      {{ getMetricExplanation(metric.metric) }}
                    </p>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Description Panel -->
        <v-col cols="3">
          <v-card v-if="selectedGroup">
            <v-card-title>{{ selectedGroup }} Explanation</v-card-title>
            <v-card-text>
              <p>{{ getGroupExplanation(selectedGroup) }}</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationService from "@/services/resultService";
import configService from "@/services/configurationService";

export default {
  components: {
    BaseLayout,
  },
  name: "RunDetail",
  props: ["runId", "configId"],
  data() {
    return {
      groupedMetrics: null,
      selectedGroup: null,
    };
  },
  mounted() {
    console.log("Config ID:", this.configId);
    console.log("Run ID:", this.runId);
    this.fetchRunMetrics();
    this.fetchConfigDetails(); // Fetch the application name from config details
  },
  methods: {
    fetchRunMetrics() {
      evaluationService
        .getResultDetail(this.configId, this.runId)
        .then((response) => {
          console.log("Fetched Run Metrics Data:", response.data);
          this.groupedMetrics = this.groupMetricsByCategory(
            response.data.metrics
          );
          console.log("Grouped Metrics:", this.groupedMetrics);

          // Set the first group as selected by default
          this.selectedGroup = Object.keys(this.groupedMetrics)[0];
        })
        .catch((error) => {
          console.error("Error fetching run metrics:", error);
        });
    },
    fetchConfigDetails() {
      configService
        .getConfigById(this.configId) // Assuming this service fetches the config details
        .then((response) => {
          this.applicationName = response.data.application_name;
        })
        .catch((error) => {
          console.error("Error fetching configuration details:", error);
        });
    },
    groupMetricsByCategory(metricsData) {
      const groupedMetrics = {};

      // Helper function to capitalize metric names
      function capitalizeFirstLetter(string) {
        return string
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");
      }

      // Iterate through each metric category and format for display
      for (const category in metricsData) {
        groupedMetrics[category] = Object.entries(metricsData[category]).map(
          ([metricName, value]) => ({
            metric: capitalizeFirstLetter(metricName),
            value,
          })
        );
      }

      return groupedMetrics;
    },
    selectGroup(groupName) {
      this.selectedGroup = groupName;
    },
    getMetricExplanation(metricName) {
      // Add explanations for different metrics
      const explanations = {
        // TODO: Update with actual descriptions form DB
        "Prediction Accuracy":
          "Measures the accuracy of the system's predictions.",
        Precision:
          "The proportion of positive identifications that were actually correct.",
        Recall:
          "The proportion of actual positives that were correctly identified.",
        "Overall System Accuracy":
          "The overall correctness of the system's outputs.",
        // Add more explanations for other metrics here
      };

      return explanations[metricName] || "No description available.";
    },
    getGroupExplanation(groupName) {
      // Add group explanations to provide more context
      const explanations = {
        Performance:
          "This category contains metrics related to the overall accuracy and precision of the AI system.", // TODO: Update with actual descriptions form DB
        Efficiency:
          "These metrics measure the resource usage, time performance, and system efficiency.",
        // Add more explanations for other groups here
      };

      return explanations[groupName] || "No description available.";
    },
    getGroupIcon(groupName) {
      // Return appropriate icons for metric groups
      const icons = {
        Performance: "mdi-chart-line",
        Efficiency: "mdi-speedometer",
        "Adaptability and Learning": "mdi-brain",
        "Collaboration and Interaction": "mdi-human-handsup",
        "Trust and Safety": "mdi-shield",
        "Robustness and Generalization": "mdi-robot",
      };
      return icons[groupName] || "mdi-information";
    },
  },
};
</script>

<style scoped>
.selected-group {
  background-color: #e0e0e0;
}
.metric-description {
  color: #757575;
  font-size: 0.875rem;
}
</style>
