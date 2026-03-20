<template>
  <v-expansion-panel>
    <v-expansion-panel-title>
      <v-icon left :color="iconColor">{{ icon }}</v-icon>
      {{ title }}
    </v-expansion-panel-title>
    <v-expansion-panel-text>
      <v-list dense>
        <MetricItem
          v-for="metric in metrics"
          :key="metric.title"
          :title="metric.title"
          :description="metric.description"
          :formula="metric.formula"
        />
      </v-list>
    </v-expansion-panel-text>
  </v-expansion-panel>
</template>

<script>
/**
 * MetricGroup Component
 *
 * Displays a group of metrics in an expandable panel.
 * Used to organize metrics by category (Effectiveness, Efficiency, etc.)
 *
 * @props {String} title - Group title
 * @props {String} icon - Material Design icon name
 * @props {String} iconColor - Icon color
 * @props {Array} metrics - Array of metric objects
 */
import MetricItem from "@/components/MetricItem.vue";

export default {
  name: "MetricGroup",
  components: {
    MetricItem,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      default: "mdi-chart-line",
    },
    iconColor: {
      type: String,
      default: "primary",
    },
    metrics: {
      type: Array,
      default: () => [],
    },
  },
};
</script>
