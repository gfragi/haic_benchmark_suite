<template>
  <BaseLayout>
    <v-container>
      <h2>Run Details for Run ID: {{ runId }}</h2>

      <v-tabs v-if="groupedMetrics">
        <v-tab v-for="(metrics, groupName) in groupedMetrics" :key="groupName">
          {{ groupName }}
        </v-tab>

        <v-tab-item
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
              <v-btn @click="showPlot(groupName)">Show Plot</v-btn>
            </v-card-text>
          </v-card>
        </v-tab-item>
      </v-tabs>

      <!-- Placeholder for charts or other visualizations -->
      <v-dialog v-model="plotDialog" max-width="800">
        <v-card>
          <v-card-title>{{ selectedGroup }} Plot</v-card-title>
          <v-card-text>
            <!-- Embed your plot here (e.g., using Chart.js or D3.js) -->
            <plot-component :groupName="selectedGroup" :runId="runId" />
          </v-card-text>
        </v-card>
      </v-dialog>
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
  name: "RunDetail",
  props: ["runId", "configId"], // Props passed from the route
  data() {
    return {
      groupedMetrics: null,
      selectedGroup: null,
      plotDialog: false,
      metricHeaders: [
        { text: "Metric", value: "metric" },
        { text: "Value", value: "value" },
      ],
    };
  },
  mounted() {
    console.log("Config ID:", this.configId); // Check that the props are passed correctly
    console.log("Run ID:", this.runId);
    this.fetchRunMetrics();
  },
  methods: {
    fetchRunMetrics() {
      evaluationService
        .getResultDetail(this.configId, this.runId) // Use props to fetch the correct data
        .then((response) => {
          this.groupedMetrics = this.groupMetricsByCategory(response.data);
        })
        .catch((error) => {
          console.error("Error fetching run metrics:", error);
        });
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

      const excludedKeys = ["id", "configuration_id", "evaluation_date"];
      const metrics = Object.keys(result)
        .filter((key) => !excludedKeys.includes(key))
        .map((key) => ({
          metric: key.replace(/_/g, " ").toUpperCase(),
          value: result[key],
        }));

      metrics.forEach((metric) => {
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

      return groupedMetrics;
    },
    showPlot(groupName) {
      this.selectedGroup = groupName;
      this.plotDialog = true;
    },
  },
};
</script>
