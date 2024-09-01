<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedGroup"
            :items="metricGroups"
            label="Select Metric Group"
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
  name: "ResultPlot",
  components: {
    BaseLayout,
    PlotlyChart,
  },
  data() {
    return {
      selectedConfigId: this.$route.params.configId,
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
    console.log("Selected Config ID:", this.selectedConfigId);
    this.fetchResults();
  },
  watch: {
    selectedGroup() {
      this.fetchResults();
    },
  },
  methods: {
    fetchResults() {
      console.log("Fetching results for Config ID:", this.selectedConfigId);
      if (this.selectedGroup) {
        resultService
          .getResultsByConfigIdAndGroup(
            this.selectedConfigId,
            this.selectedGroup
          )
          .then((response) => {
            this.results = response.data; // Assign the returned metrics
            this.updateChartData(); // Update the chart with new data
          })
          .catch((error) => {
            console.error("Error fetching results:", error);
          });
      } else {
        console.error("Config ID or Group not defined");
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
