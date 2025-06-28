<template>
  <BaseLayout>
    <v-container>
      <SurveyFilter @update:pilotTag="loadData" />
      <SurveyChart :data="aggregatedData" />
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { ref } from "vue";
import SurveyChart from "@/components/SurveyChart.vue";
import SurveyFilter from "@/components/SurveyFilter.vue";
import { fetchSurveyAggregates } from "@/services/survey";

const aggregatedData = ref({});

async function loadData(pilotTag = null) {
  const raw = await fetchSurveyAggregates(pilotTag);
  // Transform to app_version-based aggregation
  aggregatedData.value = {};

  for (const [values] of Object.entries(raw)) {
    const version = values.app_version || "Unknown";
    if (!aggregatedData.value[version]) {
      aggregatedData.value[version] = {
        avg_sus: values.avg_sus,
        avg_ethics: values.avg_ethics,
      };
    }
  }
}
loadData();
</script>
