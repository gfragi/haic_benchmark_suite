<template>
  <div class="my-6">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, defineProps, nextTick } from "vue";
import Chart from "chart.js/auto";

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  type: {
    type: String,
    default: "bar", // Accepts 'bar' or 'line'
  },
});

const chartCanvas = ref(null);
let chartInstance = null;

watch(
  () => props.data,
  async (newData) => {
    if (!newData || Object.keys(newData).length === 0) return;

    await nextTick();

    if (!chartCanvas.value) {
      console.warn("Chart canvas is not yet available");
      return;
    }

    const ctx = chartCanvas.value.getContext("2d");
    if (!ctx) {
      console.warn("Canvas context not available");
      return;
    }

    if (chartInstance) {
      chartInstance.destroy();
    }

    const labels = Object.keys(newData);
    const susData = labels.map((v) => newData[v]?.avg_sus || 0);
    const ethicsData = labels.map((v) => newData[v]?.avg_ethics || 0);

    const isLine = props.type === "line";

    chartInstance = new Chart(ctx, {
      type: props.type,
      data: {
        labels,
        datasets: [
          {
            label: "Avg SUS",
            data: susData,
            backgroundColor: isLine
              ? "rgba(54, 162, 235, 0.3)"
              : "rgba(54, 162, 235, 0.7)",
            borderColor: "rgba(54, 162, 235, 1)",
            tension: isLine ? 0.3 : 0,
            fill: isLine ? false : true,
          },
          {
            label: "Avg Ethics",
            data: ethicsData,
            backgroundColor: isLine
              ? "rgba(255, 99, 132, 0.3)"
              : "rgba(255, 99, 132, 0.7)",
            borderColor: "rgba(255, 99, 132, 1)",
            tension: isLine ? 0.3 : 0,
            fill: isLine ? false : true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
          },
        },
      },
    });
  },
  { immediate: true }
);
</script>

<style scoped>
div {
  height: 400px;
}
</style>
