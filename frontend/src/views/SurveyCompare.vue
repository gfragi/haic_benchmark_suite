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

      <!-- KPI chips -->
      <v-row v-if="ready" class="mb-2" align="center">
        <v-col cols="12" md="8">
          <div class="d-flex flex-wrap gap-2">
            <v-chip variant="flat" color="primary">
              A ({{ versionA }}): SUS {{ A.sus.toFixed(1) }}
            </v-chip>
            <v-chip variant="flat" color="primary">
              A ({{ versionA }}): Ethics {{ A.eth.toFixed(1) }}
            </v-chip>
            <v-chip variant="flat" color="secondary">
              B ({{ versionB }}): SUS {{ B.sus.toFixed(1) }}
            </v-chip>
            <v-chip variant="flat" color="secondary">
              B ({{ versionB }}): Ethics {{ B.eth.toFixed(1) }}
            </v-chip>
          </div>
        </v-col>
        <v-col cols="12" md="4" class="d-flex justify-end gap-2">
          <v-chip :color="deltaSusColor" variant="outlined">
            Δ SUS {{ deltaSUS >= 0 ? "+" : "" }}{{ deltaSUS.toFixed(1) }}
          </v-chip>
          <v-chip :color="deltaEthColor" variant="outlined">
            Δ Ethics {{ deltaETH >= 0 ? "+" : "" }}{{ deltaETH.toFixed(1) }}
          </v-chip>
        </v-col>
      </v-row>

      <v-divider class="my-3" />

      <!-- Overall chart -->
      <div v-if="ready" class="px-2">
        <SurveyChart
          :data="chartRows"
          type="bar"
          :x-label="'Version'"
          :y-label="'Average score (0–100)'"
          :legend-info="true"
          :title="chartTitle"
          :showErrorBars="false"
        />
      </div>
      <div v-else class="text-center my-8">
        <v-progress-circular indeterminate color="primary" size="36" />
      </div>

      <div v-if="ready" class="text-caption text-medium-emphasis mt-3 mb-6">
        Samples — A ({{ versionA }}): n={{ A.n }}, B ({{ versionB }}): n={{
          B.n
        }}
      </div>

      <!-- Per-question heatmap -->
      <v-card v-if="heatmapReady" class="mb-6" elevation="1">
        <v-card-title class="text-subtitle-1"
          >Per-question breakdown</v-card-title
        >
        <v-card-subtitle class="text-body-2">
          Averages per question on a 1–5 scale (darker = higher). Hover for
          exact values.
        </v-card-subtitle>
        <v-card-text>
          <div class="text-caption mb-1">SUS (Q1–Q10)</div>
          <div class="heatmap-grid mb-4">
            <div class="heatmap-cell header"></div>
            <div class="heatmap-cell header">A: {{ versionA }}</div>
            <div class="heatmap-cell header">B: {{ versionB }}</div>

            <template v-for="q in susOrder" :key="q">
              <div class="heatmap-cell qlabel">{{ susLabels[q] || q }}</div>
              <div
                class="heatmap-cell"
                :style="cellStyle(susA[q])"
                :title="`${q} · A: ${fmtOneToFive(susA[q])}`"
              >
                {{ fmtOneToFive(susA[q]) }}
              </div>
              <div
                class="heatmap-cell"
                :style="cellStyle(susB[q])"
                :title="`${q} · B: ${fmtOneToFive(susB[q])}`"
              >
                {{ fmtOneToFive(susB[q]) }}
              </div>
            </template>
          </div>

          <div class="text-caption mb-1">Ethics</div>
          <div class="heatmap-grid">
            <div class="heatmap-cell header"></div>
            <div class="heatmap-cell header">A: {{ versionA }}</div>
            <div class="heatmap-cell header">B: {{ versionB }}</div>

            <template v-for="q in ethicsOrder" :key="q">
              <div class="heatmap-cell qlabel">{{ ethicsLabels[q] || q }}</div>
              <div
                class="heatmap-cell"
                :style="cellStyle(ethA[q])"
                :title="`${q} · A: ${fmtOneToFive(ethA[q])}`"
              >
                {{ fmtOneToFive(ethA[q]) }}
              </div>
              <div
                class="heatmap-cell"
                :style="cellStyle(ethB[q])"
                :title="`${q} · B: ${fmtOneToFive(ethB[q])}`"
              >
                {{ fmtOneToFive(ethB[q]) }}
              </div>
            </template>
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import BaseLayout from "@/components/BaseLayout.vue";
import SurveyFilter from "@/components/SurveyFilter.vue";
import SurveyChart from "@/components/SurveyChart.vue";
import {
  fetchSurveyAggregates,
  fetchVersions,
  fetchQuestionAverages,
} from "@/services/survey";
import semver from "semver";

const route = useRoute();
const router = useRouter();

const pilotTag = ref(String(route.query.pilot || ""));
const versions = ref([]);
const versionA = ref("");
const versionB = ref("");
const aggregates = ref({});
const loading = ref(false);

// per-question averages (1..5)
const susA = ref({});
const susB = ref({});
const ethA = ref({});
const ethB = ref({});
const loadingHeatmap = ref(false);

// order + labels
const susOrder = [
  "sus_q1",
  "sus_q2",
  "sus_q3",
  "sus_q4",
  "sus_q5",
  "sus_q6",
  "sus_q7",
  "sus_q8",
  "sus_q9",
  "sus_q10",
];
const susLabels = {
  sus_q1: "Q1",
  sus_q2: "Q2",
  sus_q3: "Q3",
  sus_q4: "Q4",
  sus_q5: "Q5",
  sus_q6: "Q6",
  sus_q7: "Q7",
  sus_q8: "Q8",
  sus_q9: "Q9",
  sus_q10: "Q10",
};
const ethicsOrder = [
  "q_fairness",
  "q_transparency",
  "q_privacy",
  "q_accountability",
  "q_trust",
];
const ethicsLabels = {
  q_fairness: "Fairness",
  q_transparency: "Transparency",
  q_privacy: "Privacy",
  q_accountability: "Accountability",
  q_trust: "Trust",
};

async function loadHeatmap() {
  susA.value = {};
  susB.value = {};
  ethA.value = {};
  ethB.value = {};
  if (!pilotTag.value || !versionA.value || !versionB.value) return;
  loadingHeatmap.value = true;
  try {
    const [a, b] = await Promise.all([
      fetchQuestionAverages(pilotTag.value, versionA.value),
      fetchQuestionAverages(pilotTag.value, versionB.value),
    ]);
    if (a?.sus) susA.value = a.sus;
    if (a?.ethics) ethA.value = a.ethics;
    if (b?.sus) susB.value = b.sus;
    if (b?.ethics) ethB.value = b.ethics;
  } finally {
    loadingHeatmap.value = false;
  }
}

function fmtOneToFive(x) {
  if (x == null || isNaN(Number(x))) return "—";
  return Number(x).toFixed(2);
}

function cellStyle(v) {
  // v in 1..5; map to 0..1 for color intensity.
  const t = Math.max(0, Math.min(1, ((Number(v) || 0) - 1) / 4));
  const bg = `rgba(33,150,243, ${0.15 + 0.55 * t})`; // blue ramp
  const color = t > 0.6 ? "white" : "black";
  return { background: bg, color, textAlign: "center" };
}

// Load both the version list and the aggregate map whenever pilot changes
async function loadForPilot(tag) {
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
      fetchVersions(tag),
      fetchSurveyAggregates(tag),
    ]);
    const sorted = [...(vers || [])].sort((a, b) => {
      if (semver.valid(a) && semver.valid(b)) return semver.compare(a, b);
      return String(a).localeCompare(String(b));
    });
    versions.value = sorted;
    aggregates.value = aggs || {};

    const ensureInList = (v) => (sorted.includes(v) ? v : "");
    versionA.value = ensureInList(versionA.value);
    versionB.value = ensureInList(versionB.value);

    if (!versionA.value && sorted.length)
      versionA.value = sorted.at(-2) || sorted[0];
    if (!versionB.value && sorted.length)
      versionB.value = sorted.at(-1) || sorted[0];

    await loadHeatmap();
  } finally {
    loading.value = false;
  }
}

function onPilotChange(tag) {
  pilotTag.value = tag || "";
  router.replace({
    query: { ...route.query, pilot: pilotTag.value || undefined },
  });
  loadForPilot(pilotTag.value);
}

// react to URL query changes
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

// reload heatmap when versions change
watch([versionA, versionB], () => loadHeatmap());

// helpers to read a version’s metrics from the aggregate map (0..100 scale)
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
const A = computed(() => getStats(versionA.value));
const B = computed(() => getStats(versionB.value));
const deltaSUS = computed(() => B.value.sus - A.value.sus);
const deltaETH = computed(() => B.value.eth - A.value.eth);
const deltaSusColor = computed(() =>
  deltaSUS.value >= 0 ? "success" : "error"
);
const deltaEthColor = computed(() =>
  deltaETH.value >= 0 ? "success" : "error"
);

const chartTitle = computed(() =>
  pilotTag.value
    ? `${pilotTag.value} · A: ${versionA.value || "-"} vs B: ${
        versionB.value || "-"
      }`
    : "Select a pilot"
);

// Shape compatible with SurveyChart (dashboard shape)
const chartRows = computed(() => {
  if (!ready.value) return {};
  return {
    [`A: ${versionA.value}`]: {
      avg_sus: A.value.sus,
      avg_ethics: A.value.eth,
      count: A.value.n,
    },
    [`B: ${versionB.value}`]: {
      avg_sus: B.value.sus,
      avg_ethics: B.value.eth,
      count: B.value.n,
    },
  };
});

const heatmapReady = computed(
  () =>
    ready.value &&
    Object.keys(susA.value).length &&
    Object.keys(susB.value).length
);

// Initial load
loadForPilot(pilotTag.value);
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: 6px;
  align-items: stretch;
}

.heatmap-cell {
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1;
}

.heatmap-cell.header {
  font-weight: 600;
  background: rgba(0, 0, 0, 0.06);
}

.heatmap-cell.qlabel {
  font-weight: 500;
  background: rgba(0, 0, 0, 0.04);
}
</style>
