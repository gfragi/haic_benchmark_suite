<template>
  <canvas :id="chartId"></canvas>
</template>

<script>
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
} from "chart.js";

Chart.register(LineController, LineElement, PointElement, LinearScale, Title);

export default {
  props: {
    chartId: {
      type: String,
      required: true,
    },
    chartData: {
      type: Object,
      required: true,
    },
  },
  mounted() {
    this.renderChart();
  },
  watch: {
    chartData: {
      handler() {
        this.renderChart();
      },
      deep: true,
    },
  },
  methods: {
    renderChart() {
      const ctx = document.getElementById(this.chartId).getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: this.chartData,
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: "top",
            },
            title: {
              display: true,
              text: "Metric Plot",
            },
          },
        },
      });
    },
  },
};
</script>
