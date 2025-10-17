<template>
  <div v-if="pairs.length" class="w-100">
    <canvas ref="canvas"></canvas>
  </div>
  <v-alert v-else type="info" variant="tonal">No metrics to display.</v-alert>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed } from "vue";
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
} from "chart.js";
Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip);

const props = defineProps({
  metrics: { type: Object, default: () => ({}) },
});

const canvas = ref(null);
let chart;

const pairs = computed(() => {
  // order like the Streamlit bar: F, D, HCL, Tr, A, S, EL, EfficiencyScore
  const m = props.metrics || {};
  const order = ["F", "D", "HCL", "Tr", "A", "S", "EL", "EfficiencyScore"];
  return order.filter((k) => k in m).map((k) => ({ k, v: Number(m[k]) }));
});

function render() {
  if (!canvas.value) return;
  if (chart) {
    chart.destroy();
    chart = null;
  }
  if (!pairs.value.length) return;

  const labels = pairs.value.map((p) => p.k);
  const values = pairs.value.map((p) => p.v);

  chart = new Chart(canvas.value.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [{ data: values }],
    },
    options: {
      responsive: true,
      plugins: { tooltip: { enabled: true } },
      scales: {
        x: { ticks: { autoSkip: false } },
        y: { beginAtZero: true },
      },
    },
  });
}

onMounted(render);
onBeforeUnmount(() => chart && chart.destroy());
watch(() => props.metrics, render, { deep: true });
</script>

<style scoped>
.w-100 {
  width: 100%;
}
</style>
