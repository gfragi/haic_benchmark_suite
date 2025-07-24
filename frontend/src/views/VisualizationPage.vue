<template>
  <BaseLayout>
    <v-container fluid>
      <!-- Run Information Title -->
      <v-row>
        <v-col>
          <h1 class="text-h4 mb-2">
            Visualization for Configuration ID: {{ configId }}
          </h1>
          <p class="subtitle-1 mb-4">
            This page displays visualizations for the selected configuration.
            You can explore the metric groups on the left to see the
            performance, efficiency, and more.
          </p>
        </v-col>
      </v-row>

      <v-row>
        <!-- Left Sidebar for Metric Groups -->
        <v-col cols="2">
          <v-list dense>
            <v-list-item
              v-for="group in groupOptions"
              :key="group.value"
              @click="selectedGroup = group.value"
              :class="{ 'selected-group': selectedGroup === group.value }"
              style="cursor: pointer"
            >
              <v-list-item>
                <v-icon>{{ getGroupIcon(group.value) }}</v-icon>
              </v-list-item>
              <v-list-item-title class="text-caption">{{
                group.title
              }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-col>

        <!-- Main Content Area for Charts -->
        <v-col cols="10">
          <v-row>
            <v-col
              v-for="(metric, index) in selectedMetrics"
              :key="index"
              cols="10"
              md="6"
            >
              <h3 class="text-h6 mb-2">{{ metric }}</h3>
              <ChartComponent
                v-if="chartData[metric]"
                :chartId="'chart-' + index"
                :chartData="chartData[metric]"
                :chartColor="getChartColor(index)"
              />
            </v-col>
          </v-row>
        </v-col>
      </v-row>

      <!-- Back Button -->
      <v-row>
        <v-col cols="12" class="text-center">
          <v-btn color="primary" @click="goBack">Back</v-btn>
        </v-col>
      </v-row>

      <v-overlay :value="isLoading">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
      </v-overlay>

      <v-snackbar v-model="snackbar" :color="snackbarColor" top>
        {{ snackbarText }}
        <template v-slot:action="{ attrs }">
          <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
        </template>
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script>
import ChartComponent from "@/components/PlotChart.vue";
import resultService from "@/services/resultService";
import evaluationService from "@/services/evaluationService";
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  components: {
    ChartComponent,
    BaseLayout,
  },
  data() {
    return {
      configId: null,
      selectedGroup: null,
      groupOptions: [],
      groupedMetrics: {},
      chartData: {},
      labels: [],
      selectedMetrics: [],
      runData: [],
      isLoading: false,
      snackbar: false,
      snackbarText: "",
      snackbarColor: "info",
    };
  },
  mounted() {
    this.configId = this.$route.params.configId;
    this.fetchMetricGroups();
  },
  methods: {
    fetchMetricGroups() {
      this.isLoading = true;
      evaluationService
        .getMetrics()
        .then((response) => {
          this.groupedMetrics = response.data;
          this.groupOptions = Object.keys(this.groupedMetrics).map((group) => ({
            title: group,
            value: group,
          }));
          this.selectedGroup = this.groupOptions[0].value;
          this.updateSelectedMetrics();
          this.fetchData();
        })
        .catch((error) => {
          console.error("Error fetching metric groups:", error);
          this.showMessage(
            "Error fetching metric groups. Please try again.",
            "error"
          );
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    updateSelectedMetrics() {
      if (this.selectedGroup && this.groupedMetrics[this.selectedGroup]) {
        this.selectedMetrics = this.groupedMetrics[
          this.selectedGroup
        ].metrics.map((metric) => metric.name);
      } else {
        this.selectedMetrics = [];
      }
    },
    fetchData() {
      this.isLoading = true;
      resultService
        .getResultsByConfig(this.configId)
        .then((response) => {
          this.runData = response.data;
          this.labels = this.runData.map((run) => run.ai_model_version);
          this.chartData = {};
          this.runData.forEach((run) => {
            if (run.id) {
              this.fetchRunDetails(run.id);
            } else {
              console.error("Run ID is undefined or null", run);
            }
          });
        })
        .catch((error) => {
          console.error("Error fetching run data:", error);
          this.showMessage("Error fetching data. Please try again.", "error");
        })
        .finally(() => {
          this.isLoading = false;
        });
    },
    fetchRunDetails(runId) {
      resultService
        .getResultDetail(this.configId, runId)
        .then((response) => {
          const resultData = response.data;
          if (!resultData || !resultData.metrics) {
            console.error("Metrics data is missing in run details", resultData);
            return;
          }
          this.prepareChartData(resultData.metrics, runId);
        })
        .catch((error) => {
          console.error("Error fetching run details:", error);
          this.showMessage(
            "Error fetching run details. Please try again.",
            "error"
          );
        });
    },
    prepareChartData(metrics, runId) {
      if (!metrics[this.selectedGroup]) {
        console.error(
          "No metrics found for the selected group:",
          this.selectedGroup
        );
        return;
      }

      // Process labels (versions) to remove duplicates and sort
      this.labels = [...new Set(this.labels)].sort((a, b) => {
        // Compare versions as strings
        return a.localeCompare(b, undefined, {
          numeric: true,
          sensitivity: "base",
        });
      });

      this.selectedMetrics.forEach((metric, index) => {
        const metricData = metrics[this.selectedGroup][metric];
        if (metricData !== undefined) {
          if (!this.chartData[metric]) {
            this.chartData[metric] = {
              labels: this.labels,
              datasets: [
                {
                  label: metric,
                  data: new Array(this.labels.length).fill(null),
                  fill: false,
                  borderColor: this.getChartColor(index),
                  tension: 0.1,
                },
              ],
            };
          }
          const versionIndex = this.labels.indexOf(
            this.runData.find((run) => run.id === runId).ai_model_version
          );
          if (versionIndex !== -1) {
            this.chartData[metric].datasets[0].data[versionIndex] = metricData;
          }
        } else {
          console.error(
            "Metric data not found for:",
            metric,
            "in group:",
            this.selectedGroup
          );
        }
      });

      this.chartData = { ...this.chartData };
    },
    showMessage(text, color = "info") {
      this.snackbarText = text;
      this.snackbarColor = color;
      this.snackbar = true;
    },
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
    getChartColor(index) {
      const colors = [
        "#4CAF50", // Green
        "#2196F3", // Blue
        "#FFC107", // Amber
        "#E91E63", // Pink
        "#9C27B0", // Purple
        "#00BCD4", // Cyan
        "#FF5722", // Deep Orange
        "#795548", // Brown
      ];
      return colors[index % colors.length];
    },
    goBack() {
      this.$router.go(-1);
    },
  },
  watch: {
    selectedGroup() {
      this.updateSelectedMetrics();
      this.fetchData();
    },
  },
};
</script>

<style scoped>
.selected-group {
  background-color: #e0e0e0;
}
</style>
