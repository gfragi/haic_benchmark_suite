<template>
  <v-card class="ma-4 pa-4" style="height: 320px">
    <canvas ref="canvasEl"></canvas>
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
  CategoryScale,
  Title,
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
  CategoryScale,
  Title,
  Legend,
  Tooltip
);

export default {
  name: "PlotChart",
  props: {
    chartData: { type: Object, required: true }, // { labels:[], datasets:[] }
    chartType: {
      type: String,
      default: "line",
      validator: (v) => ["line", "bar"].includes(v),
    },
  },
  data: () => ({ chart: null, observer: null, isVisible: false }),
  async mounted() {
    // Render only when the canvas is actually visible
    this.observer = new IntersectionObserver(
      ([entry]) => {
        this.isVisible = entry.isIntersecting;
        if (this.isVisible) {
          this.renderChartSafely();
          this.observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );
    this.observer.observe(this.$refs.canvasEl);
  },
  beforeUnmount() {
    this.observer?.disconnect();
    this.destroyChart();
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        this.updateOrRender();
      },
    },
    chartType() {
      this.updateOrRender(true);
    },
  },
  methods: {
    async renderChartSafely() {
      await this.$nextTick();
      const canvas = this.$refs.canvasEl;
      if (!canvas || !canvas.isConnected) return;
      const ctx = canvas.getContext("2d");
      if (!ctx || !this._hasData()) return;

      this.destroyChart();
      const dataCopy = JSON.parse(JSON.stringify(this.chartData));
      this.chart = new Chart(ctx, {
        type: this.chartType,
        data: dataCopy,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false, // avoid RAF race during tab switches
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
    updateOrRender(resetType = false) {
      if (!this.isVisible) return; // wait until visible
      if (this.chart && this._hasData()) {
        if (resetType) this.chart.config.type = this.chartType;
        this.chart.data = JSON.parse(JSON.stringify(this.chartData));
        this.chart.update();
      } else {
        this.renderChartSafely();
      }
    },
    destroyChart() {
      if (this.chart) {
        this.chart.stop(); // stop animations first
        this.chart.destroy();
        this.chart = null;
      }
    },
    _hasData() {
      const d = this.chartData || {};
      return (
        Array.isArray(d.labels) &&
        d.labels.length &&
        Array.isArray(d.datasets) &&
        d.datasets.length
      );
    },
  },
};
</script>

<style scoped>
.v-card {
  position: relative;
}
canvas {
  width: 100%;
  height: 100%;
  min-height: 300px;
  display: block;
}
</style>
