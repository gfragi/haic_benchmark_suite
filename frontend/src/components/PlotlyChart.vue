<template>
  <div ref="chart"></div>
</template>

<script>
import Plotly from "plotly.js-dist";

export default {
  name: "PlotlyChart",
  props: ["data", "layout"],
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      Plotly.newPlot(this.$refs.chart, this.data, this.layout);
    },
  },
};
</script>
