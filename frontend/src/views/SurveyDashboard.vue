<template>
  <BaseLayout>
    <v-container>
      <!-- Header and Instructions -->
      <v-alert type="info" class="mb-4" dense>
        This dashboard displays average SUS and Ethics scores. You can compare
        different app versions within a pilot, or switch to pilot-level
        comparison.
      </v-alert>

      <!-- Comparison Mode Toggle -->
      <v-radio-group v-model="comparisonMode" row class="mb-4">
        <v-radio label="Compare App Versions (per Pilot)" value="versions" />
        <v-radio label="Compare Pilots (overall)" value="pilots" />
      </v-radio-group>

      <!-- Pilot Filter (only for version comparison) -->
      <SurveyFilter
        v-if="comparisonMode === 'versions'"
        @update:pilotTag="loadData"
      />

      <!-- Loading Indicator -->
      <div v-if="loading" class="text-center my-8">
        <v-progress-circular indeterminate color="primary" size="40" />
      </div>

      <!-- Chart Title -->
      <h3 v-if="!loading" class="text-h6 text-center my-4">
        {{ chartTitle }}
      </h3>

      <!-- Chart -->
      <SurveyChart
        v-if="Object.keys(aggregatedData).length"
        :data="aggregatedData"
      />

      <!-- No Data Message -->
      <div v-else-if="!loading" class="text-center my-8">
        <p>No data available.</p>
      </div>

      <!-- Export Button -->
      <v-btn class="mt-4" @click="exportData" color="primary">Export CSV</v-btn>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import BaseLayout from "@/components/BaseLayout.vue";
import SurveyFilter from "@/components/SurveyFilter.vue";
import SurveyChart from "@/components/SurveyChart.vue";
import { fetchSurveyAggregates } from "@/services/survey";
import { ref, computed } from "vue";
import debounce from "lodash.debounce";

const comparisonMode = ref("versions");
const selectedPilot = ref(null);
const aggregatedData = ref({});
const loading = ref(false);

const chartTitle = computed(() => {
  if (comparisonMode.value === "versions") {
    return `Avg SUS & Ethics per App Version for "${
      selectedPilot.value || "..."
    }"`;
  } else {
    return "Avg SUS & Ethics per Pilot";
  }
});

const loadData = debounce(async (pilotTag = null) => {
  loading.value = true;
  try {
    selectedPilot.value = pilotTag;
    const raw = await fetchSurveyAggregates(
      comparisonMode.value === "versions" ? pilotTag : null
    );
    aggregatedData.value = raw;
  } catch (error) {
    console.error("Failed to load data:", error);
    aggregatedData.value = {};
  } finally {
    loading.value = false;
  }
}, 300);

// Initial load: default is all pilots
loadData();

function exportData() {
  const csv = Object.entries(aggregatedData.value)
    .map(
      ([key, vals]) =>
        `${key},${vals.avg_sus.toFixed(2)},${vals.avg_ethics.toFixed(2)},${
          vals.count
        }`
    )
    .join("\n");

  const header =
    comparisonMode.value === "versions"
      ? "App Version,Avg SUS,Avg Ethics,Count\n"
      : "Pilot,Avg SUS,Avg Ethics,Count\n";

  const blob = new Blob([header + csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "survey_aggregates.csv";
  link.click();
}
</script>
