<template>
  <canvas ref="chartCanvas"></canvas>
</template>

<script setup>
import { ref, watch, defineProps } from "vue";
import Chart from "chart.js/auto";
const props = defineProps({ data: Object });

const chartCanvas = ref(null);
let chartInstance;

watch(
  () => props.data,
  (newData) => {
    if (chartInstance) chartInstance.destroy();
    renderChart(newData);
  },
  { immediate: true }
);

function renderChart(data) {
  const appVersions = Object.keys(data);
  const susData = appVersions.map((v) => data[v].avg_sus);
  const ethicsData = appVersions.map((v) => data[v].avg_ethics);

  chartInstance = new Chart(chartCanvas.value, {
    type: "bar",
    data: {
      labels: appVersions,
      datasets: [
        {
          label: "Avg SUS",
          data: susData,
          backgroundColor: "rgba(54, 162, 235, 0.7)",
        },
        {
          label: "Avg Ethics",
          data: ethicsData,
          backgroundColor: "rgba(255, 99, 132, 0.7)",
        },
      ],
    },
    options: {
      scales: {
        y: { beginAtZero: true, max: 100 },
      },
    },
  });
}
</script>
