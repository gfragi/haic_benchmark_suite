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
              Application: {{ applicationName }}, Application Version:
              {{ applicationVersion }} <br />
              AI Model: {{ aiModelName }}, AI Model Version:
              {{ aiModelVersion }}
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
              v-for="(group, groupName) in groupedMetrics"
              :key="groupName"
              @click="selectGroup(groupName)"
              :class="{ 'selected-group': selectedGroup === groupName }"
              style="cursor: pointer"
            >
              <v-list-item-icon>
                <v-icon>{{ getGroupIcon(groupName) }}</v-icon>
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
                  v-for="(metric, index) in groupedMetrics[selectedGroup]
                    .metrics"
                  :key="index"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ metric.name }}</v-list-item-title>
                    <v-list-item-subtitle>
                      <strong>Description:</strong>
                      {{ metric.description || "No description available" }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle>
                      <strong>Value:</strong>
                      {{
                        metric.value !== null && metric.value !== undefined
                          ? metric.value
                          : "No value available"
                      }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Description Panel for the selected group -->
        <v-col cols="3">
          <v-card v-if="selectedGroup">
            <v-card-title>{{ selectedGroup }} Explanation</v-card-title>
            <v-card-text>
              <p>{{ getGroupExplanation(selectedGroup) }}</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Back Button -->
      <v-row>
        <v-col cols="12" class="text-center">
          <v-btn color="primary" @click="goBack">Back</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationService from "@/services/evaluationService";
import configurationService from "@/services/configurationService";

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
      applicationName: "",
      applicationVersion: "", // To display application name
      aiModelName: "", // To display AI model name
      aiModelVersion: "", // To display AI model version
    };
  },
  mounted() {
    this.fetchRunMetrics(); // Fetch the metrics
    this.fetchConfigDetails(); // Fetch the application name (optional)
  },
  methods: {
    // Fetch the grouped metrics from the database
    fetchRunMetrics() {
      evaluationService
        .getMetrics() // Call the /evaluate/metrics endpoint
        .then((response) => {
          console.log("Fetched Metrics Data:", response.data);
          this.groupedMetrics = response.data; // Backend response already grouped
          console.log("Grouped Metrics:", this.groupedMetrics);

          // Fetch metric values and match them
          this.fetchMetricValues();

          // Set the first group as selected by default
          this.selectedGroup = Object.keys(this.groupedMetrics)[0];
        })
        .catch((error) => {
          console.error("Error fetching run metrics:", error);
        });
    },

    // Fetch the metric values from the relevant JSON file
    fetchMetricValues() {
      evaluationService
        .getResultDetail(this.configId, this.runId)
        .then((response) => {
          const metricValues = response.data.metrics;
          this.applicationVersion = response.data.app_version;
          this.aiModelVersion = response.data.ai_model_version;

          console.log("Fetched Metric Values from JSON:", metricValues);

          // Iterate through groups and match values with their metrics
          for (const groupName in this.groupedMetrics) {
            const metricsList = this.groupedMetrics[groupName].metrics;

            // Iterate through each metric in the group
            metricsList.forEach((metric) => {
              console.log("Checking metric:", metric.name); // Debugging

              // Check if the metric name exists in the JSON for the group and handle `0` values properly
              if (
                metricValues[groupName] &&
                metricValues[groupName][metric.name] !== undefined &&
                metricValues[groupName][metric.name] !== null
              ) {
                metric.value = metricValues[groupName][metric.name];
                console.log(`Assigned value to ${metric.name}:`, metric.value); // Debugging
              } else {
                metric.value = "No value available"; // Fallback if no value found
                console.log(`${metric.name} not found in fetched values`); // Debugging
              }
            });
          }

          // Force Vue to detect changes (optional, depending on your reactivity setup)
          this.groupedMetrics = { ...this.groupedMetrics };

          console.log(
            "Updated Grouped Metrics with values:",
            this.groupedMetrics
          );
        })
        .catch((error) => {
          console.error("Error fetching metric values from JSON:", error);
        });
    },
    fetchConfigDetails() {
      configurationService
        .getConfigById(this.configId)
        .then((response) => {
          this.applicationName = response.data.application_name;
          this.aiModelName = response.data.ai_model_name;
        })
        .catch((error) => {
          console.error("Error fetching configuration details:", error);
        });
    },

    // Handle group selection
    selectGroup(groupName) {
      this.selectedGroup = groupName;
    },

    // Return the group explanation from the API response
    getGroupExplanation(groupName) {
      return (
        this.groupedMetrics[groupName]?.group_description ||
        "No description available."
      );
    },

    // Return appropriate icons for metric groups
    getGroupIcon(groupName) {
      const icons = {
        Effectiveness: "mdi-chart-line",
        Efficiency: "mdi-speedometer",
        "Adaptability and Learning": "mdi-brain",
        "Collaboration and Interaction": "mdi-human-handsup",
        "Trust and Safety": "mdi-shield",
        "Robustness and Generalization": "mdi-robot",
      };
      return icons[groupName] || "mdi-information";
    },

    // Navigate back to the previous page
    goBack() {
      this.$router.go(-1);
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
