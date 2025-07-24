<template>
  <Bar :data="chartData" />
</template>

<script>
import { Bar } from "vue-chartjs";
import { computed } from "vue";

export default {
  props: {
    metrics: Object,
  },
  setup(props) {
    const chartData = computed(() => ({
      labels: Object.keys(props.metrics || {}),
      datasets: [
        {
          label: "Metric Values",
          data: Object.values(props.metrics || {}),
          backgroundColor: "#42A5F5",
        },
      ],
    }));
    return { chartData, Bar };
  },
};
</script>
