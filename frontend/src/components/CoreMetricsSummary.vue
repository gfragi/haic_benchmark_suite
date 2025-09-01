<!-- src/components/CoreMetricsSummary.vue -->
<template>
  <v-card>
    <v-card-title class="text-h6">Core HAIC Metrics v1 — Summary</v-card-title>
    <v-card-subtitle v-if="params"
      >rt_max={{ params.rt_max }} • baseline_s={{
        params.baseline_s ?? "—"
      }}</v-card-subtitle
    >
    <v-divider />
    <v-card-text>
      <v-row dense>
        <template v-for="(group, pillar) in grouped" :key="pillar">
          <v-col cols="12" class="mt-2">
            <div class="text-subtitle-2 font-medium">{{ pillar }}</div>
          </v-col>

          <v-col v-for="m in group" :key="m.key" cols="12" md="6" lg="4">
            <v-card variant="tonal" class="pa-3">
              <div class="text-body-2">{{ m.meta.label }}</div>
              <div v-if="isPercentMetric(m.key)" class="mt-2">
                <v-progress-linear
                  :model-value="Math.max(0, Math.min(100, percentValue(m.key)))"
                  height="10"
                  rounded
                />
                <div class="text-caption mt-1">{{ displayValue(m.key) }}</div>
              </div>
              <div v-else class="text-body-1 mt-1">
                {{ displayValue(m.key) }}
              </div>
            </v-card>
          </v-col>
        </template>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { computed } from "vue";
import { CORE_METRIC_META } from "@/utils/metricMappingUtil";

const props = defineProps({
  summary: { type: Object, required: true }, // { F,D,HCL,Tr,A,S,EL,EfficiencyScore }
  params: { type: Object, default: null }, // { rt_max, baseline_s }
});

const metricKeys = Object.keys(CORE_METRIC_META);

const grouped = computed(() => {
  const out = {};
  for (const k of metricKeys) {
    if (!(k in props.summary)) continue;
    const meta = CORE_METRIC_META[k];
    out[meta.pillar] ??= [];
    out[meta.pillar].push({ key: k, meta });
  }
  return out;
});

function isPercentMetric(k) {
  return ["HCL", "Tr", "S", "EfficiencyScore"].includes(k);
}
function percentValue(k) {
  const v = Number(props.summary?.[k] ?? 0);
  return Math.round(v * 100);
}
function displayValue(k) {
  const v = props.summary?.[k];
  const meta = CORE_METRIC_META[k];
  return meta?.fmt ? meta.fmt(v) : String(v);
}
</script>
