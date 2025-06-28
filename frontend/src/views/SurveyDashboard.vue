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

      <!-- Chart Type Switch -->
      <v-switch
        v-model="isLineChart"
        :label="`Chart type: ${isLineChart ? 'line' : 'bar'}`"
        class="mb-4"
      />

      <!-- Pilot Filter (only for version comparison) -->
      <SurveyFilter
        v-if="comparisonMode === 'versions'"
        @update:pilotTag="loadData"
      />

      <!-- Loading Indicator -->
      <div v-if="loading" class="text-center my-8">
        <v-progress-circular indeterminate color="primary" size="40" />
      </div>

      <!-- Chart Title and Count -->
      <div v-if="!loading" class="text-center my-4">
        <h3 class="text-h6">{{ chartTitle }}</h3>
        <p class="text-caption">Total surveys: {{ totalSurveys }}</p>
      </div>

      <!-- Chart -->
      <SurveyChart
        v-if="Object.keys(aggregatedData).length"
        :data="sortedAggregatedData"
        :type="chartType"
      />

      <!-- No Data Message -->
      <div v-else-if="!loading" class="text-center my-8">
        <p>No data available.</p>
      </div>

      <!-- Export Button -->
      <v-btn class="mt-4" @click="exportData" color="primary">Export CSV</v-btn>

      <!-- Evaluation Questions -->
      <v-expansion-panels class="mt-6">
        <v-expansion-panel>
          <v-expansion-panel-title>SUS Questions</v-expansion-panel-title>
          <v-expansion-panel-text>
            <ol>
              <li>I think I would like to use this system frequently.</li>
              <li>I found the system unnecessarily complex.</li>
              <li>I thought the system was easy to use.</li>
              <li>
                I think I would need the support of a technical person to use
                this system.
              </li>
              <li>
                I found the various functions in this system were well
                integrated.
              </li>
              <li>
                I thought there was too much inconsistency in this system.
              </li>
              <li>
                I would imagine most people would learn to use this system
                quickly.
              </li>
              <li>I found the system very difficult to use.</li>
              <li>I felt very confident using the system.</li>
              <li>
                I needed to learn many things before I could get going with this
                system.
              </li>
            </ol>
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel>
          <v-expansion-panel-title>Ethics Questions</v-expansion-panel-title>
          <v-expansion-panel-text>
            <ol>
              <li>
                Fairness: The system handles different tasks or users without
                bias.
              </li>
              <li>
                Transparency: I understand how the system/AI arrives at its
                decisions.
              </li>
              <li>
                Privacy: I feel confident that personal data is protected.
              </li>
              <li>
                Accountability: It is clear who or what is responsible for
                errors.
              </li>
              <li>
                Trust: Overall, I trust the system to operate ethically and in
                my best interest.
              </li>
            </ol>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
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
import semver from "semver";

const comparisonMode = ref("versions");
const selectedPilot = ref(null);
const aggregatedData = ref({});
const loading = ref(false);
const isLineChart = ref(false);
const chartType = computed(() => (isLineChart.value ? "line" : "bar"));

const totalSurveys = computed(() =>
  Object.values(aggregatedData.value).reduce(
    (acc, val) => acc + (val.count || 0),
    0
  )
);

const chartTitle = computed(() => {
  if (comparisonMode.value === "versions") {
    return `Avg SUS & Ethics per App Version for "${
      selectedPilot.value || "..."
    }"`;
  } else {
    return "Avg SUS & Ethics per Pilot";
  }
});

const sortedAggregatedData = computed(() => {
  const entries = Object.entries(aggregatedData.value);
  if (comparisonMode.value === "versions") {
    return Object.fromEntries(
      entries.sort(([a], [b]) => {
        if (semver.valid(a) && semver.valid(b)) {
          return semver.compare(a, b);
        }
        return a.localeCompare(b); // fallback
      })
    );
  }
  return aggregatedData.value;
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
