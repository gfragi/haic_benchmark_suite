<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedGroup"
            :items="metricGroups"
            label="Select Metric Group"
            @change="fetchResults"
            solo
            hide-details
          ></v-select>
        </v-col>
      </v-row>

      <v-row v-if="results">
        <v-col cols="12">
          <PlotlyChart :data="chartData" :layout="chartLayout"></PlotlyChart>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import PlotlyChart from "@/components/PlotlyChart.vue";
import resultService from "@/services/resultService";
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  name: "ResultView",
  components: {
    BaseLayout,
    PlotlyChart,
  },
  data() {
    return {
      selectedConfigId: this.$route.params.configId, // Assuming configId is passed as a route parameter
      metricGroups: [
        "Performance",
        "Efficiency",
        "Adaptability and Learning",
        "Collaboration and Interaction",
        "Trust and Safety",
        "Robustness and Generalization",
      ],
      selectedGroup: "Performance",
      results: null,
      chartData: [],
      chartLayout: {},
    };
  },
  mounted() {
    this.fetchResults();
  },
  methods: {
    fetchResults() {
      if (this.selectedGroup) {
        resultService
          .getResultsByConfigIdAndGroup(
            this.selectedConfigId,
            this.selectedGroup
          )
          .then((response) => {
            this.results = response.data;
            this.updateChartData();
          })
          .catch((error) => {
            console.error("Error fetching results:", error);
          });
      }
    },
    updateChartData() {
      const metrics = Object.keys(this.results); // e.g., ['accuracy', 'precision', 'recall']
      this.chartData = metrics.map((metric) => {
        return {
          x: this.results[metric].map((_, i) => i + 1), // Versions or steps
          y: this.results[metric],
          mode: "lines+markers",
          name: metric,
        };
      });

      this.chartLayout = {
        title: `${this.selectedGroup} Metrics Over Time`,
        xaxis: {
          title: "Version",
        },
        yaxis: {
          title: "Normalized Metric Value",
        },
      };
    },
  },
};
</script>

<style scoped>
.chart-container {
  margin-top: 25px;
  position: relative;
  height: 400px;
}
</style>
