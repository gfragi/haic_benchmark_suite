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
        <v-col cols="6">
          <v-select
            v-model="selectedGroup"
            :items="groupOptions"
            label="Select a metric group to plot"
            @change="fetchData"
          ></v-select>
        </v-col>

        <!-- X-Axis Dropdown (Evaluation Date/Model Version) -->
        <v-col cols="6">
          <v-select
            v-model="selectedXAxis"
            :items="xAxisOptions"
            label="Select X-Axis (Evaluation Date/AI Model Version)"
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
      selectedXAxis: "evaluation_date",
      groupOptions: [],
      xAxisOptions: [
        { title: "Evaluation Date", value: "evaluation_date" },
        { title: "AI Model Version", value: "ai_model_version" },
      ],
      groupedMetrics: {},
      chartData: {},
      labels: [],
      selectedMetrics: [],
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
          this.selectedMetrics = this.groupedMetrics[
            this.selectedGroup
          ].metrics.map((metric) => metric.name);
          this.fetchData();
        })
        .catch((error) => {
          console.error("Error fetching metric groups:", error);
        });
    },
    fetchData() {
      resultService
        .getResultsByConfig(this.configId)
        .then((response) => {
          const runs = response.data;
          this.labels = runs.map((run) => run[this.selectedXAxis]);
          this.chartData = {}; // Clear existing chart data
          runs.forEach((run) => {
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
          if (!this.selectedMetrics || this.selectedMetrics.length === 0) {
            console.error("No selected metrics to prepare chart data.");
            return;
          }
          this.prepareChartData(resultData.metrics);
        })
        .catch((error) => {
          console.error("Error fetching run details:", error);
        });
    },
    prepareChartData(metrics) {
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
      if (!this.selectedMetrics || this.selectedMetrics.length === 0) {
        console.error("No selected metrics to prepare chart data.");
        return;
      }
      this.chartData = {};
      this.selectedMetrics.forEach((metric) => {
        console.log("Processing metric:", metric);
        console.log(
          "Available metrics for group:",
          metrics[this.selectedGroup]
        );
        // Use the original metric name to access the data
        const metricData = metrics[this.selectedGroup][metric];
        if (metricData !== undefined) {
          this.chartData[metric] = {
            labels: this.labels,
            datasets: [
              {
                label: metric,
                data: metricData, // Adjust this based on your data structure
                fill: false,
                borderColor: "rgb(75, 192, 192)",
                tension: 0.1,
              },
            ],
          };
          console.log(
            "Prepared chartData for plotting:",
            JSON.stringify(this.chartData[metric], null, 2)
          );
        } else {
          console.error(
            "Metric data not found for:",
            metric,
            "in group:",
            this.selectedGroup
          );
        }
      });
      console.log("Final chartData:", JSON.stringify(this.chartData, null, 2));
    },
  },
};
</script>
