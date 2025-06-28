<template>
  <v-card class="ma-4 pa-4">
    <!-- Use a dynamic canvas ID -->
    <canvas :id="chartId"></canvas>
  </v-card>
</template>

<script>
import {
  Chart,
  LineController,
  BarController,
  LineElement,
  PointElement,
  BarElement,
  LinearScale,
  Title,
  CategoryScale,
  Legend,
  Tooltip,
} from "chart.js";

Chart.register(
  LineController,
  BarController,
  LineElement,
  PointElement,
  BarElement,
  LinearScale,
  Title,
  CategoryScale,
  Legend,
  Tooltip
);

export default {
  name: "PlotChart",
  props: {
    chartId: {
      type: String,
      required: true,
    },
    chartData: {
      type: Object,
      required: true,
    },
    chartType: {
      type: String,
      default: "line",
      validator: (value) => ["line", "bar"].includes(value),
    },
  },
  data() {
    return {
      chartInstance: null,
    };
  },
  mounted() {
    this.renderChart();
  },
  watch: {
    chartData: {
      handler: "renderChart",
      deep: true,
    },
    chartType: "renderChart",
  },
  methods: {
    renderChart() {
      const ctx = document.getElementById(this.chartId);
      if (!ctx) {
        console.error("Canvas element not found for chart ID:", this.chartId);
        return;
      }

      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      const dataCopy = JSON.parse(JSON.stringify(this.chartData));

      this.chartInstance = new Chart(ctx, {
        type: this.chartType,
        data: dataCopy,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "top" },
            tooltip: { mode: "index", intersect: false },
          },
          scales: {
            x: { title: { display: true, text: "Group" } },
            y: { beginAtZero: true, title: { display: true, text: "Value" } },
          },
        },
      });
    },
  },
};
</script>

<style scoped>
canvas {
  min-height: 300px;
}
</style>
