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
import { nextTick, markRaw, toRaw } from "vue";

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
Chart.defaults.animation = false;

export default {
  name: "PlotChart",
  props: {
    chartData: { type: Object, required: true },
    chartType: {
      type: String,
      default: "line",
      validator: (v) => ["line", "bar"].includes(v),
    },
    chartOptions: {
      type: Object,
      default: () => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                // when data point is null -> show N/A
                return ctx.raw === null || ctx.raw === undefined
                  ? "N/A"
                  : `${ctx.raw}`;
              },
            },
          },
          legend: { display: true },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              // keep tick labels readable; show “N/A” only in tooltip
              callback: (v) => v,
            },
          },
        },
      }),
    },
  },
  data: () => ({ chart: null, isRendering: false, queuePending: false }),
  async mounted() {
    await this.renderChartSafely();
  },
  beforeUnmount() {
    this.destroyChart();
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        this.updateOrRender();
      },
    },
    chartOptions: {
      deep: true,
      handler() {
        this.updateOrRender(true);
      },
    },
    chartType() {
      this.updateOrRender(true);
    },
  },
  methods: {
    _plain(obj) {
      const raw = toRaw(obj);
      try {
        return structuredClone(raw);
      } catch {
        return JSON.parse(JSON.stringify(raw));
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
    async renderChartSafely() {
      if (this.isRendering) return;
      this.isRendering = true;
      await nextTick();

      const el = this.$refs.canvasEl;
      const ctx = el && el.isConnected ? el.getContext("2d") : null;
      if (!ctx || !this._hasData()) {
        this.isRendering = false;
        return;
      }

      this.destroyChart();
      const data = this._plain(this.chartData);
      const options = this._plain(this.chartOptions);

      this.chart = markRaw(
        new Chart(ctx, { type: this.chartType, data, options })
      );
      this.isRendering = false;
    },
    updateOrRender(resetAll = false) {
      if (this.queuePending) return;
      this.queuePending = true;
      queueMicrotask(() => {
        this.queuePending = false;
        if (this.chart && this._hasData()) {
          if (resetAll) this.chart.config.type = this.chartType;
          this.chart.data = this._plain(this.chartData);
          if (resetAll) this.chart.options = this._plain(this.chartOptions);
          this.chart.update();
        } else {
          this.renderChartSafely();
        }
      });
    },
    destroyChart() {
      if (this.chart) {
        this.chart.stop?.();
        this.chart.destroy();
        this.chart = null;
      }
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
