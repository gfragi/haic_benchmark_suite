<template>
  <BaseLayout>
    <v-container class="py-6" max-width="1100">
      <v-toolbar flat>
        <v-toolbar-title>Survey Compare (SUS & Ethics)</v-toolbar-title>
        <v-spacer />
        <v-btn variant="text" :to="{ name: 'SurveyDashboard' }">
          <v-icon start>mdi-view-dashboard</v-icon> Dashboard
        </v-btn>
      </v-toolbar>

      <v-card rounded="xl" elevation="2">
        <v-card-text>
          <v-row class="mb-2" align="center">
            <v-col cols="12" md="4">
              <v-text-field
                label="Pilot tag"
                v-model="pilotTag"
                density="comfortable"
                prepend-inner-icon="mdi-tag"
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                label="Version A"
                :items="versionOptions"
                v-model="verA"
                density="comfortable"
                prepend-inner-icon="mdi-alpha-a-box"
              />
            </v-col>
            <v-col cols="12" md="3">
              <v-select
                label="Version B"
                :items="versionOptions"
                v-model="verB"
                density="comfortable"
                prepend-inner-icon="mdi-alpha-b-box"
              />
            </v-col>
            <v-col cols="12" md="2">
              <v-btn
                color="primary"
                class="mt-1"
                :loading="loading"
                @click="load"
              >
                <v-icon start>mdi-refresh</v-icon> Load
              </v-btn>
            </v-col>
          </v-row>

          <v-alert type="info" variant="tonal" class="mb-4">
            Pick a pilot and two app versions to compare. Deltas are B − A. CI
            non-overlap is marked as “likely meaningful”.
          </v-alert>

          <v-row>
            <v-col cols="12" md="6">
              <v-card variant="outlined" rounded="xl">
                <v-card-title class="text-subtitle-1">SUS</v-card-title>
                <v-card-text>
                  <div class="text-h5">
                    {{ pretty(avgSUSA) }} → {{ pretty(avgSUSB) }}
                    <v-chip
                      size="small"
                      :color="deltaSUS >= 0 ? 'success' : 'error'"
                      class="ml-2"
                    >
                      Δ {{ pretty(deltaSUS) }}
                    </v-chip>
                  </div>
                  <div class="mt-1">
                    A (n={{ aCount }}) CI±{{ pretty(susCIA) }} | B (n={{
                      bCount
                    }}) CI±{{ pretty(susCIB) }}
                    <v-chip
                      size="x-small"
                      class="ml-2"
                      :color="susMeaningful ? 'primary' : 'default'"
                    >
                      {{ susMeaningful ? "likely meaningful" : "unclear" }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="6">
              <v-card variant="outlined" rounded="xl">
                <v-card-title class="text-subtitle-1">Ethics</v-card-title>
                <v-card-text>
                  <div class="text-h5">
                    {{ pretty(avgEthicsA) }} → {{ pretty(avgEthicsB) }}
                    <v-chip
                      size="small"
                      :color="deltaEthics >= 0 ? 'success' : 'error'"
                      class="ml-2"
                    >
                      Δ {{ pretty(deltaEthics) }}
                    </v-chip>
                  </div>
                  <div class="mt-1">
                    A (n={{ aCount }}) CI±{{ pretty(ethicsCIA) }} | B (n={{
                      bCount
                    }}) CI±{{ pretty(ethicsCIB) }}
                    <v-chip
                      size="x-small"
                      class="ml-2"
                      :color="ethicsMeaningful ? 'primary' : 'default'"
                    >
                      {{ ethicsMeaningful ? "likely meaningful" : "unclear" }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-divider class="my-6" />

          <!-- Simple bars; you can replace with your SurveyChart if you want -->
          <div class="text-subtitle-1 mb-2">Bar preview</div>
          <canvas ref="canvas" height="120"></canvas>
        </v-card-text>
      </v-card>

      <v-snackbar v-model="snack.show" :timeout="4000" :color="snack.color">
        {{ snack.text }}
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch, computed } from "vue";
import BaseLayout from "@/components/BaseLayout.vue";
import { useRoute, useRouter } from "vue-router";
import {
  fetchSurveyAggregatesByPilot,
  computeDeltas,
} from "@/services/surveyCompareService";
import Chart from "chart.js/auto";

const route = useRoute();
const router = useRouter();

const pilotTag = ref(route.query.pilot || "");
const verA = ref(route.query.a || "");
const verB = ref(route.query.b || "");
const loading = ref(false);
const snack = ref({ show: false, text: "", color: "success" });

// data from backend
const agg = ref({});
const versionOptions = computed(() => Object.keys(agg.value || {}));

// picked versions’ stats
const A = computed(() => agg.value?.[verA.value] || {});
const B = computed(() => agg.value?.[verB.value] || {});

const avgSUSA = computed(() => A.value.avg_sus ?? 0);
const avgSUSB = computed(() => B.value.avg_sus ?? 0);
const avgEthicsA = computed(() => A.value.avg_ethics ?? 0);
const avgEthicsB = computed(() => B.value.avg_ethics ?? 0);
const susCIA = computed(() => A.value.sus_ci95 ?? 0);
const susCIB = computed(() => B.value.sus_ci95 ?? 0);
const ethicsCIA = computed(() => A.value.ethics_ci95 ?? 0);
const ethicsCIB = computed(() => B.value.ethics_ci95 ?? 0);
const aCount = computed(() => A.value.count ?? 0);
const bCount = computed(() => B.value.count ?? 0);

const deltas = computed(() => computeDeltas(A.value, B.value));
const deltaSUS = computed(() => deltas.value.delta.sus || 0);
const deltaEthics = computed(() => deltas.value.delta.ethics || 0);
const susMeaningful = computed(() => deltas.value.susLikelyMeaningful);
const ethicsMeaningful = computed(() => deltas.value.ethicsLikelyMeaningful);

function pretty(x) {
  return Number(x ?? 0).toFixed(1);
}

async function load() {
  if (!pilotTag.value) {
    snack.value = {
      show: true,
      text: "Enter a pilot tag first.",
      color: "warning",
    };
    return;
  }
  loading.value = true;
  try {
    agg.value = await fetchSurveyAggregatesByPilot(pilotTag.value);
    // default selects if empty
    const keys = Object.keys(agg.value);
    if (!verA.value && keys[0]) verA.value = keys[0];
    if (!verB.value && keys[1]) verB.value = keys[1] || keys[0];
    drawChart();
    // keep URL shareable
    router.replace({
      query: { pilot: pilotTag.value, a: verA.value, b: verB.value },
    });
  } catch (e) {
    snack.value = {
      show: true,
      text: "Failed to load aggregates.",
      color: "error",
    };
  } finally {
    loading.value = false;
  }
}

const canvas = ref(null);
let chart;

function drawChart() {
  // guard: if component is going away or canvas absent, skip
  if (!canvas.value || !verA.value || !verB.value) return;

  const labels = ["SUS", "Ethics"];
  const aVals = [avgSUSA.value, avgEthicsA.value];
  const bVals = [avgSUSB.value, avgEthicsB.value];

  if (chart) chart.destroy();
  chart = new Chart(canvas.value, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: `A: ${verA.value}`, data: aVals },
        { label: `B: ${verB.value}`, data: bVals },
      ],
    },
    options: {
      responsive: true,
      animation: false, // optional: reduces race conditions on fast nav
      plugins: { legend: { position: "top" } },
      scales: { y: { beginAtZero: true, suggestedMax: 100 } },
    },
  });
}

onBeforeUnmount(() => {
  if (chart) {
    chart.destroy();
    chart = null;
  }
});

watch([verA, verB], () => drawChart());
onMounted(() => {
  load();
});
</script>
