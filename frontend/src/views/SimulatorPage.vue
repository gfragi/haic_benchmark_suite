<template>
  <BaseLayout>
    <template #sidebar>
      <v-navigation-drawer permanent width="360">
        <v-toolbar flat density="comfortable" title="Simulator"></v-toolbar>
        <v-divider />
        <v-container>
          <v-select
            label="Select Config"
            :items="configOptions"
            v-model="selectedConfig"
            density="comfortable"
            prepend-inner-icon="mdi-file-document"
          />
          <v-text-field
            label="Seed (optional)"
            v-model="seed"
            type="number"
            density="comfortable"
            prepend-inner-icon="mdi-counter"
          />
          <v-btn
            color="primary"
            class="mt-2"
            :loading="running"
            @click="runSim"
          >
            <v-icon start>mdi-play</v-icon> Run
          </v-btn>

          <v-divider class="my-4" />

          <v-btn variant="text" @click="refreshConfigs">
            <v-icon start>mdi-refresh</v-icon> Refresh Configs
          </v-btn>
          <v-btn variant="text" @click="refreshRuns">
            <v-icon start>mdi-folder</v-icon> Browse Past Runs
          </v-btn>
        </v-container>
      </v-navigation-drawer>
    </template>

    <v-container fluid>
      <v-tabs v-model="tab" bg-color="transparent">
        <v-tab value="live">Live Run</v-tab>
        <v-tab value="browse">Browse Runs</v-tab>
        <v-tab value="viz">Visualize</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <!-- Live Run -->
        <v-window-item value="live">
          <v-row>
            <v-col cols="12" md="8">
              <v-card class="mb-4">
                <v-card-title>Run Summary</v-card-title>
                <v-card-text>
                  <div v-if="result">
                    <p class="text-body-1">{{ headline }}</p>
                    <ul class="pl-4">
                      <li v-for="(b, i) in bullets" :key="i" v-html="b"></li>
                    </ul>
                    <div class="mt-2">
                      <v-chip
                        v-for="a in result.agents"
                        :key="a"
                        size="small"
                        class="mr-2"
                        >{{ a }}</v-chip
                      >
                    </div>
                  </div>
                  <div v-else>
                    <v-alert type="info" variant="tonal"
                      >Run a simulation to see the summary.</v-alert
                    >
                  </div>
                </v-card-text>
              </v-card>

              <v-card class="mb-4">
                <v-card-title>Metrics</v-card-title>
                <v-card-text>
                  <v-row v-if="result">
                    <v-col
                      cols="6"
                      md="3"
                      v-for="(val, key) in compactMetrics"
                      :key="key"
                    >
                      <v-sheet
                        class="pa-3 text-center"
                        elevation="1"
                        rounded="lg"
                      >
                        <div class="text-caption text-medium-emphasis">
                          {{ key }}
                        </div>
                        <div class="text-h6">{{ formatNum(val) }}</div>
                      </v-sheet>
                    </v-col>
                  </v-row>
                  <v-alert v-else type="info" variant="tonal"
                    >No metrics yet.</v-alert
                  >
                </v-card-text>
              </v-card>

              <v-card>
                <v-card-title>Decisions (latest 200)</v-card-title>
                <v-card-text>
                  <v-data-table
                    :items="(result?.decisions || []).slice(-200)"
                    :headers="decisionHeaders"
                    density="compact"
                    :items-per-page="10"
                    class="text-caption"
                  />
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="4">
              <v-card class="mb-4">
                <v-card-title>Download</v-card-title>
                <v-card-text>
                  <v-btn
                    :disabled="!result"
                    @click="downloadJson"
                    prepend-icon="mdi-download"
                    >Export JSON</v-btn
                  >
                </v-card-text>
              </v-card>

              <v-card>
                <v-card-title>Run Meta</v-card-title>
                <v-card-text v-if="result">
                  <div><strong>Task:</strong> {{ result.task }}</div>
                  <div>
                    <strong>Environment:</strong> {{ result.environment }}
                  </div>
                  <div><strong>Seed:</strong> {{ result.seed ?? "—" }}</div>
                  <div>
                    <strong>Config Hash:</strong>
                    {{ result.config_hash || "—" }}
                  </div>
                  <div>
                    <strong>Config Path:</strong>
                    {{ result.config_path || "—" }}
                  </div>
                </v-card-text>
                <v-card-text v-else>
                  <v-alert type="info" variant="tonal">No run yet.</v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Browse -->
        <v-window-item value="browse">
          <v-row>
            <v-col cols="12" md="4">
              <v-card>
                <v-card-title>Past Runs</v-card-title>
                <v-card-text>
                  <v-list density="compact" nav>
                    <v-list-item
                      v-for="f in metricFiles"
                      :key="f"
                      :value="f"
                      @click="loadRun(f)"
                    >
                      <v-list-item-title>{{ f }}</v-list-item-title>
                    </v-list-item>
                  </v-list>
                  <v-btn variant="text" @click="refreshRuns">
                    <v-icon start>mdi-refresh</v-icon> Refresh
                  </v-btn>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="8">
              <v-card>
                <v-card-title>Selected Run</v-card-title>
                <v-card-text v-if="browsed">
                  <p class="text-body-1">{{ browsedHeadline }}</p>
                  <ul class="pl-4">
                    <li
                      v-for="(b, i) in browsedBullets"
                      :key="i"
                      v-html="b"
                    ></li>
                  </ul>
                </v-card-text>
                <v-card-text v-else>
                  <v-alert type="info" variant="tonal"
                    >Pick a file to preview insights.</v-alert
                  >
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-window-item>

        <!-- Visualize (slot for your existing chart components) -->
        <v-window-item value="viz">
          <v-alert type="info" variant="tonal" class="mb-4">
            Hook your existing <code>SimulationMetricsChart</code> /
            <code>PlotChart</code> here if desired.
          </v-alert>
        </v-window-item>
      </v-window>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import BaseLayout from "@/components/BaseLayout.vue";
import { listConfigs } from "@/services/configurationService";
import {
  simulate,
  listMetrics,
  loadMetrics,
} from "@/services/simulationService";
import {
  summarizeRunBrief,
  deriveAuxRates,
  interpretMetrics,
} from "@/utils/insightsUtil";

const tab = ref("live");
const running = ref(false);
const seed = ref("");
const configOptions = ref([]);
const selectedConfig = ref(null);

const result = ref(null);
const metricFiles = ref([]);
const browsed = ref(null);

const decisionHeaders = [
  { title: "t", key: "t", width: 80 },
  { title: "agent", key: "agent", width: 120 },
  { title: "action", key: "action", width: 140 },
  { title: "actor", key: "actor_type", width: 80 },
  { title: "latency_ms", key: "latency_ms", width: 110 },
  { title: "duration_s", key: "duration_s", width: 100 },
  { title: "correct", key: "correct", width: 85 },
  { title: "off_role", key: "off_role_action", width: 90 },
  { title: "event", key: "event_type", width: 120 },
];

const headline = computed(() =>
  result.value ? summarizeRunBrief(result.value) : ""
);
const bullets = computed(() => {
  if (!result.value) return [];
  const aux = deriveAuxRates(result.value);
  return interpretMetrics(result.value.metrics || {}, aux);
});

const compactMetrics = computed(() => {
  if (!result.value?.metrics) return {};
  const m = result.value.metrics;
  return {
    F: m.F,
    HCL: m.HCL,
    Tr: m.Tr,
    A: m.A,
    S: m.S,
    EL: m.EL,
    Eff: m.EfficiencyScore,
  };
});

const browsedHeadline = computed(() =>
  browsed.value ? summarizeRunBrief(browsed.value) : ""
);
const browsedBullets = computed(() => {
  if (!browsed.value) return [];
  const aux = deriveAuxRates(browsed.value);
  return interpretMetrics(browsed.value.metrics || {}, aux);
});

function formatNum(v) {
  const n = Number(v);
  if (Number.isNaN(n)) return "—";
  if (Math.abs(n) >= 100) return n.toFixed(0);
  if (Math.abs(n) >= 1) return n.toFixed(2);
  return n.toFixed(3);
}

async function refreshConfigs() {
  configOptions.value = await listConfigs();
  if (!selectedConfig.value && configOptions.value.length) {
    selectedConfig.value = configOptions.value[0];
  }
}

async function refreshRuns() {
  metricFiles.value = await listMetrics();
}

async function runSim() {
  if (!selectedConfig.value) return;
  running.value = true;
  try {
    result.value = await simulate(selectedConfig.value, seed.value);
    tab.value = "live";
  } finally {
    running.value = false;
    await refreshRuns();
  }
}

async function loadRun(file) {
  browsed.value = await loadMetrics(file);
  tab.value = "browse";
}

function downloadJson() {
  if (!result.value) return;
  const blob = new Blob([JSON.stringify(result.value, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const fname = `${(result.value.task || "run").replace(
    /\s+/g,
    "_"
  )}_${Date.now()}.json`;
  a.download = fname;
  a.click();
  URL.revokeObjectURL(url);
}

onMounted(async () => {
  await refreshConfigs();
  await refreshRuns();
});
</script>
