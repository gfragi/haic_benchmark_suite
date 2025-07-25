<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script setup>
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
);

// Props
const props = defineProps({
  metrics: {
    type: Object,
    required: true,
  },
});

// Create chart data from metrics
const chartData = {
  labels: Object.keys(props.metrics),
  datasets: [
    {
      label: "Simulation Metrics",
      backgroundColor: "#42A5F5",
      data: Object.values(props.metrics),
    },
  ],
};

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    title: {
      display: true,
      text: "Simulation Metrics",
    },
  },
};
</script>
