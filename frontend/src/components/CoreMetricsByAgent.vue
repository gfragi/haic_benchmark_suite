<!-- src/components/CoreMetricsByAgent.vue -->
<template>
  <v-card>
    <v-card-title class="text-h6">Per-Agent Breakdown</v-card-title>
    <v-divider />
    <v-data-table
      :headers="headers"
      :items="rows"
      density="compact"
      class="text-caption"
    />
  </v-card>
</template>

<script setup>
import { computed } from "vue";
import { CORE_METRIC_META } from "@/utils/metricMappingUtil";

const props = defineProps({
  byAgent: { type: Object, required: true }, // { agent: {F,...}, ... }
});

const headers = computed(() => {
  const metricHeaders = Object.keys(CORE_METRIC_META).map((k) => ({
    title: CORE_METRIC_META[k].label,
    value: k,
  }));
  return [{ title: "Agent", value: "agent" }, ...metricHeaders];
});

const rows = computed(() => {
  const items = [];
  for (const [agent, metrics] of Object.entries(props.byAgent || {})) {
    const row = { agent };
    for (const k of Object.keys(CORE_METRIC_META)) {
      const meta = CORE_METRIC_META[k];
      row[k] = meta.fmt ? meta.fmt(metrics?.[k]) : metrics?.[k];
    }
    items.push(row);
  }
  return items;
});
</script>
