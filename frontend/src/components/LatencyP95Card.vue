<template>
  <div class="card">
    <h3>AI Latency p50 / p90 / p95 by {{ payload.group_key }}</h3>
    <canvas ref="canvas"></canvas>
    <div class="muted mt-2">SLA (AI): {{ payload.sla_ms }} ms</div>
  </div>
</template>

<script>
import { onMounted, ref, watch } from "vue";
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
} from "chart.js";
Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip
);

export default {
  name: "LatencyP95Card",
  props: { payload: { type: Object, required: true } },
  setup(props) {
    const canvas = ref(null);
    let chart;

    const draw = () => {
      if (!props.payload?.labels?.length) return;
      const { labels, series, data, sla_ms } = props.payload;

      const datasets = series.map((s, i) => ({
        label: s.toUpperCase(),
        data: data[i],
      }));

      if (chart) chart.destroy();
      chart = new Chart(canvas.value, {
        type: "bar",
        data: { labels, datasets },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            tooltip: { mode: "index", intersect: false },
          },
          scales: {
            y: {
              title: { display: true, text: "Latency (ms)" },
              beginAtZero: true,
            },
          },
        },
      });

      // draw SLA line
      const ctx = chart.ctx;
      chart.once("render", () => {
        const yScale = chart.scales.y;
        const y = yScale.getPixelForValue(sla_ms);
        ctx.save();
        ctx.strokeStyle = "#cc0000";
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        ctx.moveTo(yScale.left, y);
        ctx.lineTo(chart.scales.x.right, y);
        ctx.stroke();
        ctx.restore();
      });
    };

    onMounted(draw);
    watch(() => props.payload, draw, { deep: true });
    return { canvas };
  },
};
</script>

<style scoped>
.card {
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.muted {
  font-size: 12px;
  opacity: 0.7;
}
</style>
