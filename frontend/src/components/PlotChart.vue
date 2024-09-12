<template>
  <v-card class="ma-4 pa-4">
    <canvas :id="chartId"></canvas>
  </v-card>
</template>

<script>
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
  CategoryScale,
  Legend,
  Tooltip,
} from "chart.js";

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  Title,
  CategoryScale,
  Legend,
  Tooltip
);

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
    chartColor: {
      type: String,
      default: "rgb(75, 192, 192)",
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
      const ctx = document.getElementById(this.chartId);
      if (!ctx) {
        console.error("Canvas element not found for chart ID:", this.chartId);
        return;
      }

      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      this.chartInstance = new Chart(ctx, {
        type: "line",
        data: {
          ...this.chartData,
          datasets: this.chartData.datasets.map((dataset) => ({
            ...dataset,
            borderColor: this.chartColor,
          })),
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "top",
              labels: {
                font: {
                  size: 14,
                  weight: "bold",
                },
              },
            },
            title: {
              display: true,
              text: this.chartData.datasets[0].label,
              font: {
                size: 18,
                weight: "bold",
              },
            },
            tooltip: {
              enabled: true,
              mode: "index",
              intersect: false,
            },
          },
          scales: {
            x: {
              type: "category",
              title: {
                display: true,
                text: "AI Model Version",
                font: {
                  size: 14,
                  weight: "bold",
                },
              },
              ticks: {
                font: {
                  size: 12,
                },
              },
            },
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: "Value",
                font: {
                  size: 14,
                  weight: "bold",
                },
              },
              ticks: {
                font: {
                  size: 12,
                },
              },
            },
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
