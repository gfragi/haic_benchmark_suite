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
  CategoryScale, // Import CategoryScale
} from "chart.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
  CategoryScale
); // Register CategoryScale

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
      console.log("Rendering chart with ID:", this.chartId);
      console.log("Chart data:", JSON.stringify(this.chartData, null, 2));

      if (
        !this.chartData ||
        !this.chartData.datasets ||
        this.chartData.datasets.length === 0
      ) {
        console.error(
          "Invalid chart data structure for chart ID:",
          this.chartId
        );
        return;
      }

      const ctx = document.getElementById(this.chartId);
      if (!ctx) {
        console.error("Canvas element not found for chart ID:", this.chartId);
        return;
      }

      // Clear previous chart instance if it exists
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      this.chartInstance = new Chart(ctx, {
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
          scales: {
            x: {
              type: "category", // Ensure the x-axis uses the category scale
            },
          },
        },
      });

      console.log("Chart instance created:", this.chartInstance);
    },
  },
};
</script>
