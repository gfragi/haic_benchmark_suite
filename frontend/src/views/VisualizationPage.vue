<template>
  <BaseLayout>
    <v-container>
      <!-- Page Title -->
      <v-row>
        <v-col cols="12">
          <h2>Visualization for Configuration ID: {{ configId }}</h2>
        </v-col>
      </v-row>

      <!-- Metric Group Dropdown -->
      <v-row>
        <v-col cols="12">
          <v-select
            v-model="selectedGroup"
            :items="groupOptions"
            label="Select a metric group to plot"
            @change="fetchData"
          ></v-select>
        </v-col>
      </v-row>

      <!-- Render Charts for Each Metric in the Selected Group -->
      <v-row v-if="selectedGroup && Object.keys(chartData).length > 0">
        <v-col
          v-for="(metric, index) in selectedMetrics"
          :key="index"
          cols="12"
          md="6"
        >
          <ChartComponent
            v-if="chartData[metric]"
            :chartId="'chart-' + index"
            :chartData="chartData[metric]"
          />
          <div v-else>No data available for {{ metric }}</div>
        </v-col>
      </v-row>
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
      runData: [], // Add this to store all run data
    };
  },
  mounted() {
    this.configId = this.$route.params.configId;
    this.fetchMetricGroups();
    this.fetchData();
  },
  methods: {
    fetchMetricGroups() {
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
      resultService
        .getResultsByConfig(this.configId)
        .then((response) => {
          this.runData = response.data;
          this.labels = this.runData.map((run) => run.ai_model_version);
          this.chartData = {}; // Clear existing chart data
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
        });
    },
    fetchRunDetails(runId) {
      console.log("Fetching details for run ID:", runId);
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
        });
    },
    prepareChartData(metrics, runId) {
      console.log(
        "Preparing chart data for metrics:",
        JSON.stringify(metrics, null, 2)
      );
      if (!metrics[this.selectedGroup]) {
        console.error(
          "No metrics found for the selected group:",
          this.selectedGroup
        );
        return;
      }

      this.selectedMetrics.forEach((metric) => {
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
                  borderColor: "rgb(75, 192, 192)",
                  tension: 0.1,
                },
              ],
            };
          }
          const runIndex = this.runData.findIndex((run) => run.id === runId);
          if (runIndex !== -1) {
            this.chartData[metric].datasets[0].data[runIndex] = metricData;
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

      // Force update of chartData
      this.chartData = { ...this.chartData };
      console.log("Final chartData:", JSON.stringify(this.chartData, null, 2));
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
