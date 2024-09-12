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

      <!-- Debugging Section: Display Raw Data for Debugging -->
      <v-row>
        <v-col cols="12">
          <pre>{{ groupedMetrics }}</pre>
          <pre>{{ labels }}</pre>
          <pre>{{ chartData }}</pre>
        </v-col>
      </v-row>

      <!-- Render Charts for Each Metric in the Selected Group -->
      <v-row v-if="selectedGroup">
        <v-col
          v-for="(metric, index) in selectedMetrics"
          :key="index"
          cols="12"
          md="6"
        >
          <ChartComponent
            :chartId="'chart-' + index"
            :chartData="chartData[metric]"
          />
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
      if (!metrics[this.selectedGroup]) {
        console.error("No metrics found for the selected group.");
        return;
      }
      if (!this.selectedMetrics || this.selectedMetrics.length === 0) {
        console.error("No selected metrics to prepare chart data.");
        return;
      }
      this.chartData = {};
      this.selectedMetrics.forEach((metric) => {
        const metricKey = metric.replace(/ /g, "_").toLowerCase();
        if (
          metrics[this.selectedGroup] &&
          metrics[this.selectedGroup][metricKey]
        ) {
          this.chartData[metric] = {
            labels: this.labels,
            datasets: [
              {
                label: metric,
                data: metrics[this.selectedGroup][metricKey],
                fill: false,
                borderColor: "rgb(75, 192, 192)",
                tension: 0.1,
              },
            ],
          };
        }
      });
    },
  },
};
</script>
