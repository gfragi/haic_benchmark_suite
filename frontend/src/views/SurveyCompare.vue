<template>
  <BaseLayout>
    <v-container>
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <div class="text-h6">Compare Versions</div>
          <div class="text-body-2 text-medium-emphasis">
            Select a pilot and two app versions to compare average SUS & Ethics.
          </div>
        </div>
        <v-btn
          variant="text"
          :to="{ name: 'SurveyDashboard' }"
          prepend-icon="mdi-arrow-left"
        >
          Back to Dashboard
        </v-btn>
      </div>

      <v-row class="mb-2">
        <v-col cols="12" md="4">
          <!-- Pilot selector (reuse your existing component if you want) -->
          <SurveyFilter @update:pilotTag="onPilotChange" />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            :items="versions"
            v-model="versionA"
            label="Version A"
            prepend-inner-icon="mdi-alpha-a-circle-outline"
            :disabled="!versions.length"
          />
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            :items="versions"
            v-model="versionB"
            label="Version B"
            prepend-inner-icon="mdi-alpha-b-circle-outline"
            :disabled="!versions.length"
          />
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <!-- Chart -->
      <div v-if="ready" class="px-2">
        <SurveyChart
          :data="chartRows"
          type="bar"
          :x-label="'Metric'"
          :y-label="'Average score (0–100)'"
          :legend-info="true"
          :title="chartTitle"
          :showErrorBars="false"
        />
      </div>

      <div v-else class="text-center my-8">
        <v-progress-circular indeterminate color="primary" size="36" />
      </div>

      <div v-if="countsNote" class="text-caption text-medium-emphasis mt-3">
        {{ countsNote }}
      </div>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import BaseLayout from "@/components/BaseLayout.vue";
import SurveyFilter from "@/components/SurveyFilter.vue";
import SurveyChart from "@/components/SurveyChart.vue";
import { fetchSurveyAggregates, fetchVersions } from "@/services/survey";
import semver from "semver";

const route = useRoute();
const router = useRouter();

const pilotTag = ref(String(route.query.pilot || ""));
const versions = ref([]); // <-- JS, no TS generic
const versionA = ref("");
const versionB = ref("");
const aggregates = ref({});
const loading = ref(false);

async function loadForPilot(tag) {
  // Clear state when no pilot selected
  if (!tag) {
    versions.value = [];
    versionA.value = "";
    versionB.value = "";
    aggregates.value = {};
    return;
  }

  loading.value = true;
  try {
    const [vers, aggs] = await Promise.all([
      fetchVersions(tag), // GET /survey/versions?pilot_tag=tag
      fetchSurveyAggregates(tag), // GET /survey/aggregate?pilot_tag=tag
    ]);

    const sorted = [...(vers || [])].sort((a, b) => {
      if (semver.valid(a) && semver.valid(b)) return semver.compare(a, b);
      return String(a).localeCompare(String(b));
    });

    versions.value = sorted;
    aggregates.value = aggs || {};

    // Preselect last two versions if not already chosen or now invalid
    const ensureInList = (v) => (sorted.includes(v) ? v : "");
    versionA.value = ensureInList(versionA.value);
    versionB.value = ensureInList(versionB.value);

    if (!versionA.value && sorted.length)
      versionA.value = sorted.at(-2) || sorted[0];
    if (!versionB.value && sorted.length)
      versionB.value = sorted.at(-1) || sorted[0];
  } finally {
    loading.value = false;
  }
}

function onPilotChange(tag) {
  pilotTag.value = tag || "";
  // keep URL in sync so back/forward works
  router.replace({
    query: { ...route.query, pilot: pilotTag.value || undefined },
  });
  loadForPilot(pilotTag.value);
}

// react to URL changes (?pilot=...)
watch(
  () => route.query.pilot,
  (q) => {
    const tag = String(q || "");
    if (tag !== pilotTag.value) {
      pilotTag.value = tag;
      loadForPilot(tag);
    }
  }
);

// helpers to read a version’s metrics from the aggregate map
function getStats(version) {
  const node = aggregates.value?.[version];
  if (!node) return { sus: 0, eth: 0, n: 0 };
  return {
    sus: Number(node.avg_sus ?? 0),
    eth: Number(node.avg_ethics ?? 0),
    n: Number(node.count ?? 0),
  };
}

const ready = computed(
  () =>
    !loading.value && !!pilotTag.value && !!versionA.value && !!versionB.value
);

const chartTitle = computed(() =>
  pilotTag.value
    ? `${pilotTag.value} · A: ${versionA.value || "-"} vs B: ${
        versionB.value || "-"
      }`
    : "Select a pilot"
);

const chartRows = computed(() => {
  if (!ready.value) return {};
  const A = getStats(versionA.value);
  const B = getStats(versionB.value);

  return {
    [`A: ${versionA.value}`]: {
      avg_sus: A.sus,
      avg_ethics: A.eth,
      count: A.n,
    },
    [`B: ${versionB.value}`]: {
      avg_sus: B.sus,
      avg_ethics: B.eth,
      count: B.n,
    },
  };
});

const countsNote = computed(() => {
  if (!ready.value) return "";
  const A = getStats(versionA.value);
  const B = getStats(versionB.value);
  return `Samples — A (${versionA.value}): n=${A.n}, B (${versionB.value}): n=${B.n}`;
});

// Initial load
loadForPilot(pilotTag.value);
</script>
