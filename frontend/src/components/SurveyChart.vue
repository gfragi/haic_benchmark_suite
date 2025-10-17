<template>
  <div class="w-100">
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from "vue";
import Chart from "chart.js/auto";

const props = defineProps({
  data: { type: Object, required: true }, // { labelKey: { avg_sus, sus_ci95, avg_ethics, ethics_ci95, count } }
  type: { type: String, default: "bar" }, // 'bar' | 'line'
});

const canvas = ref(null);
let chart;

function buildDatasets(obj) {
  const labels = Object.keys(obj);
  const sus = labels.map((k) => obj[k]?.avg_sus ?? 0);
  const ethics = labels.map((k) => obj[k]?.avg_ethics ?? 0);
  const susCI = labels.map((k) => obj[k]?.sus_ci95 ?? 0);
  const ethicsCI = labels.map((k) => obj[k]?.ethics_ci95 ?? 0);
  const counts = labels.map((k) => obj[k]?.count ?? 0);

  return {
    labels,
    datasets: [
      {
        label: "Avg SUS",
        data: sus,
        // custom fields used by plugins
        _ci: susCI,
        _counts: counts,
      },
      {
        label: "Avg Ethics",
        data: ethics,
        _ci: ethicsCI,
        _counts: counts,
      },
    ],
  };
}

/** Plugin to draw 95% CI whiskers for bar charts */
const ciWhiskerPlugin = {
  id: "ciWhiskerPlugin",
  afterDatasetsDraw(chart) {
    // removed args, pluginOptions
    if (chart.config.type !== "bar") return;
    const { ctx, scales } = chart; // removed chartArea
    ctx.save();
    ctx.lineWidth = 1;

    chart.data.datasets.forEach((ds, di) => {
      const meta = chart.getDatasetMeta(di);
      if (!meta?.data) return;
      const ciArr = ds._ci || [];
      meta.data.forEach((barEl, i) => {
        const ci = ciArr[i] || 0;
        const value = ds.data[i] || 0;
        if (!barEl || !Number.isFinite(ci)) return;

        const x = barEl.x;
        // removed yMid
        const yTop = scales.y.getPixelForValue(value + ci);
        const yBottom = scales.y.getPixelForValue(value - ci);

        // vertical
        ctx.beginPath();
        ctx.moveTo(x, yTop);
        ctx.lineTo(x, yBottom);
        ctx.stroke();

        // caps
        const cap = Math.max(6, barEl.width * 0.35);
        ctx.beginPath();
        ctx.moveTo(x - cap / 2, yTop);
        ctx.lineTo(x + cap / 2, yTop);
        ctx.moveTo(x - cap / 2, yBottom);
        ctx.lineTo(x + cap / 2, yBottom);
        ctx.stroke();
      });
    });
    ctx.restore();
  },
};

/** Plugin to draw N labels (n=…) above the tallest bar per category */
const countLabelsPlugin = {
  id: "countLabelsPlugin",
  afterDatasetsDraw(chart) {
    if (chart.config.type !== "bar") return;
    const { ctx } = chart; // removed 'scales'
    const labels = chart.data.labels || [];
    if (!labels.length) return;

    const dsWithCounts = chart.data.datasets.find((d) =>
      Array.isArray(d._counts)
    );
    if (!dsWithCounts) return;
    const counts = dsWithCounts._counts;

    ctx.save();
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";
    ctx.font = `${12 * (window.devicePixelRatio || 1)}px sans-serif`;

    labels.forEach((_, i) => {
      let topY = Infinity;
      let centerX = null;
      chart.data.datasets.forEach((_, di) => {
        const meta = chart.getDatasetMeta(di);
        const el = meta?.data?.[i];
        if (el) {
          centerX = el.x;
          topY = Math.min(topY, el.y);
        }
      });
      if (centerX == null || !isFinite(topY)) return;
      ctx.fillText(`n=${counts?.[i] ?? 0}`, centerX, topY - 4);
    });

    ctx.restore();
  },
};

function draw() {
  if (!canvas.value) return;
  const { labels, datasets } = buildDatasets(props.data);
  if (chart) chart.destroy();
  chart = new Chart(canvas.value, {
    type: props.type || "bar",
    data: { labels, datasets },
    options: {
      responsive: true,
      animation: false,
      plugins: {
        legend: { position: "top" },
        title: { display: false },
      },
      scales: {
        y: { beginAtZero: true, suggestedMax: 100 },
      },
    },
    plugins: [ciWhiskerPlugin, countLabelsPlugin],
  });
}

onMounted(draw);
watch(() => [props.data, props.type], draw, { deep: true });
onBeforeUnmount(() => {
  if (chart) chart.destroy();
});
</script>
