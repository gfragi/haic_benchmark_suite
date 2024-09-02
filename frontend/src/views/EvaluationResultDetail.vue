<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Result Details</h2>
      <v-tabs v-model="activeTab">
        <v-tab v-for="(group, index) in metricGroups" :key="index">
          {{ group }}
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="activeTab">
        <v-tab-item v-for="(group, index) in metricGroups" :key="index">
          <v-row>
            <v-col cols="12">
              <PlotlyChart
                :data="chartData[group]"
                :layout="chartLayout[group]"
              ></PlotlyChart>
            </v-col>
            <v-col cols="12">
              <v-data-table
                :headers="metricHeaders"
                :items="getMetrics(group)"
                class="elevation-1"
              >
                <template v-slot:[`item.metric`]="{ item }">
                  {{ item.metric }}
                </template>
                <template v-slot:[`item.value`]="{ item }">
                  {{ item.value }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>
        </v-tab-item>
      </v-tabs-items>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import PlotlyChart from "@/components/PlotlyChart.vue";
import evaluationService from "@/services/resultService";

export default {
  components: {
    BaseLayout,
    PlotlyChart,
  },
  data() {
    return {
      activeTab: 0,
      results: {},
      metricGroups: [
        "Performance",
        "Efficiency",
        "Adaptability and Learning",
        "Collaboration and Interaction",
        "Trust and Safety",
        "Robustness and Generalization",
      ],
      chartData: {},
      chartLayout: {},
      metricHeaders: [
        { text: "Metric", value: "metric" },
        { text: "Value", value: "value" },
      ],
    };
  },
  mounted() {
    this.fetchResultDetail();
  },
  methods: {
    fetchResultDetail() {
      const resultId = this.$route.params.resultId;
      evaluationService
        .getEvaluationResultsByConfig(resultId)
        .then((response) => {
          this.results = response.data || {}; // Ensure results are always an object
          console.log("Fetched Results: ", this.results);
          this.prepareChartsAndTables();
        })
        .catch((error) => {
          console.error("Error fetching evaluation result detail:", error);
        });
    },
    getMetrics(group) {
      if (!this.results || !this.results[group]) {
        return [];
      }

      const metrics = this.results[group];
      return Object.keys(metrics).map((key) => ({
        metric: key.replace(/_/g, " ").toUpperCase(),
        value: metrics[key],
      }));
    },
    prepareChartsAndTables() {
      this.metricGroups.forEach((group) => {
        const metrics = this.results[group] || {}; // Default to an empty object if undefined
        this.chartData[group] = this.prepareChartData(metrics);
        this.chartLayout[group] = {
          title: `${group} Metrics`,
          xaxis: { title: "Metric" },
          yaxis: { title: "Value" },
        };
      });
    },
    prepareChartData(metrics) {
      return Object.keys(metrics).map((metric) => ({
        x: [metric],
        y: [metrics[metric]],
        type: "bar",
        name: metric,
      }));
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
