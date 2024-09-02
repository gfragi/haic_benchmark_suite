<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col cols="12" md="6">
          <v-select
            v-model="selectedMetric"
            :items="availableMetrics"
            label="Select Metric"
            @change="fetchHistoricalData"
          ></v-select>
        </v-col>
      </v-row>

      <v-row v-if="chartData.length">
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
  name: "HistoricalMetrics",
  components: {
    BaseLayout,
    PlotlyChart,
  },
  data() {
    return {
      selectedMetric: null,
      availableMetrics: [
        "Prediction Accuracy",
        "Precision",
        "Recall",
        "Overall System Accuracy",
        "Response Time",
        "Teaching Efficiency",
        // Add other metrics...
      ],
      chartData: [],
      chartLayout: {},
    };
  },
  methods: {
    fetchHistoricalData() {
      if (!this.selectedMetric) return;

      resultService
        .getHistoricalDataForMetric(this.selectedMetric)
        .then((response) => {
          const historicalData = response.data;
          this.chartData = [
            {
              x: historicalData.map((entry) => entry.date),
              y: historicalData.map((entry) => entry.value),
              type: "scatter",
              mode: "lines+markers",
              name: this.selectedMetric,
            },
          ];
          this.chartLayout = {
            title: `${this.selectedMetric} Over Time`,
            xaxis: { title: "Date" },
            yaxis: { title: this.selectedMetric },
          };
        })
        .catch((error) => {
          console.error("Error fetching historical data:", error);
        });
    },
  },
};
</script>
