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
});

const chartCanvas = ref(null);
let chartInstance = null;

watch(
  () => props.data,
  async (newData) => {
    // Prevent rendering with no data
    if (!newData || Object.keys(newData).length === 0) return;

    // Wait for canvas to render
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

    // Destroy old chart
    if (chartInstance) {
      chartInstance.destroy();
    }

    // Prepare chart data
    const labels = Object.keys(newData);
    const susData = labels.map((v) => newData[v]?.avg_sus || 0);
    const ethicsData = labels.map((v) => newData[v]?.avg_ethics || 0);

    chartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
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
