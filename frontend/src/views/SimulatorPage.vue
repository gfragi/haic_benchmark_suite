<template>
  <BaseLayout>
    <!-- Sidebar -->
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

          <!-- Single, consistent entry point -->
          <v-btn variant="text" @click="openYaml" ref="yamlBtn">
            <v-icon start>mdi-note-text</v-icon>
            Paste YAML config
          </v-btn>
        </v-container>
      </v-navigation-drawer>
    </template>

    <!-- Tabs -->
    <v-tabs v-model="tab" bg-color="transparent">
      <v-tab value="build">Build</v-tab>
      <v-tab value="live">Live Run</v-tab>
      <v-tab value="browse">Browse Runs</v-tab>
      <v-tab value="viz">Visualize</v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <!-- ================== BUILD TAB ================== -->
      <v-window-item value="build">
        <v-row>
          <v-col cols="12" md="4">
            <v-card class="mb-4">
              <v-card-title>Agents & Metrics</v-card-title>
              <v-card-text>
                <v-alert
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="mb-4"
                >
                  Add at least one <strong>human</strong> and one
                  <strong>ai</strong> agent. <br />rt_max scales
                  Human-Centeredness (HCL). baseline_s enables Effort Loss (EL).
                </v-alert>

                <!-- Mode switch -->
                <div class="text-subtitle-2 mb-1">Execution Mode</div>
                <v-radio-group v-model="mode" inline class="mb-3">
                  <v-radio label="Adapter-driven" value="adapter" />
                  <v-radio
                    label="Scripted (use actions below)"
                    value="scripted"
                  />
                </v-radio-group>

                <v-select
                  class="mb-3"
                  label="Environment"
                  :items="envChoices"
                  v-model="builder.environment"
                  :disabled="isScripted"
                />

                <div class="text-subtitle-2">Agents</div>
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Profile</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(ag, i) in builder.agents" :key="ag.id">
                      <td>
                        <v-text-field
                          v-model="ag.id"
                          hide-details
                          density="compact"
                          :rules="[req]"
                          :hint="'Unique handle (e.g., human1, ai1)'"
                          persistent-hint
                        />
                      </td>
                      <td>
                        <v-text-field
                          v-model="ag.name"
                          hide-details
                          density="compact"
                          :rules="[req]"
                          :hint="'Label (e.g., Radiologist, AI Assistant)'"
                          persistent-hint
                        />
                      </td>
                      <td>
                        <v-select
                          :items="['human', 'ai']"
                          v-model="ag.type"
                          hide-details
                          density="compact"
                          :rules="[req]"
                        />
                      </td>
                      <td>
                        <v-text-field
                          v-model="ag.profile"
                          hide-details
                          density="compact"
                          :hint="'Free text (e.g., junior, gpt)'"
                          persistent-hint
                        />
                      </td>
                      <td>
                        <v-btn
                          icon
                          size="x-small"
                          @click="builder.agents.splice(i, 1)"
                        >
                          <v-icon color="error">mdi-delete</v-icon>
                        </v-btn>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
                <v-btn
                  size="small"
                  class="mt-2"
                  @click="
                    builder.agents.push({
                      id: `agent-${Date.now()}`,
                      name: 'Agent',
                      type: 'human',
                      profile: 'default',
                    })
                  "
                >
                  <v-icon start>mdi-plus</v-icon> Add Agent
                </v-btn>

                <v-divider class="my-4" />

                <div class="text-subtitle-2">
                  Metrics Parameters
                  <v-tooltip
                    text="Used only for metrics computation (not for sim logic)."
                  >
                    <template #activator="{ props }"
                      ><v-icon size="16" v-bind="props" class="ml-1"
                        >mdi-help-circle-outline</v-icon
                      ></template
                    >
                  </v-tooltip>
                </div>
                <v-text-field
                  v-model.number="builder.metrics.rt_max"
                  type="number"
                  label="rt_max"
                  append-inner="s"
                  density="comfortable"
                  :hint="'Upper bound for typical human reaction time. Default 5s.'"
                  persistent-hint
                />
                <v-text-field
                  v-model.number="builder.metrics.baseline_s"
                  type="number"
                  label="baseline_s (s, optional)"
                  density="comfortable"
                  :hint="'Benchmark total time for EL/EfficiencyScore (optional).'"
                  persistent-hint
                />

                <div class="mt-2">
                  <v-btn
                    color="primary"
                    class="mr-2"
                    :loading="building"
                    @click="generateAndRun"
                  >
                    <v-icon start>mdi-play</v-icon> Generate Config & Run
                  </v-btn>
                  <!-- Secondary: preview YAML prefilled from builder -->
                  <v-btn variant="text" @click="openYaml">
                    <v-icon start>mdi-eye</v-icon>
                    Preview YAML
                  </v-btn>
                </div>

                <v-alert v-if="buildErr" type="error" class="mt-2">
                  {{ buildErr }}
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="8">
            <v-card class="mb-4">
              <v-card-title>Environment</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="builder.name"
                      label="Name"
                      density="comfortable"
                      :rules="[req]"
                    />
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="builder.version"
                      label="Version"
                      density="comfortable"
                      :rules="[req]"
                    />
                  </v-col>
                </v-row>

                <v-divider class="my-3" />

                <div class="d-flex align-center justify-space-between">
                  <div class="text-subtitle-2">
                    Tasks
                    <v-tooltip
                      text="A task groups related actions (e.g., 'Review & Decision')."
                    >
                      <template #activator="{ props }"
                        ><v-icon size="16" v-bind="props" class="ml-1"
                          >mdi-help-circle-outline</v-icon
                        ></template
                      >
                    </v-tooltip>
                  </div>
                  <v-btn size="small" @click="addTask"
                    ><v-icon start>mdi-plus</v-icon> Add Task</v-btn
                  >
                </div>

                <v-expansion-panels multiple class="mt-2">
                  <v-expansion-panel
                    v-for="(t, ti) in builder.tasks"
                    :key="t.id"
                  >
                    <v-expansion-panel-title>
                      <div
                        class="d-flex align-center w-100 justify-space-between"
                      >
                        <v-text-field
                          v-model="t.name"
                          label="Task Name"
                          hide-details
                          density="compact"
                          class="ma-0 pa-0"
                          :rules="[req]"
                        />
                        <div>
                          <v-btn
                            icon
                            size="small"
                            @click.stop="moveTask(ti, -1)"
                            :disabled="ti === 0"
                            ><v-icon>mdi-arrow-up</v-icon></v-btn
                          >
                          <v-btn
                            icon
                            size="small"
                            @click.stop="moveTask(ti, 1)"
                            :disabled="ti === builder.tasks.length - 1"
                            ><v-icon>mdi-arrow-down</v-icon></v-btn
                          >
                          <v-btn icon size="small" @click.stop="removeTask(ti)"
                            ><v-icon color="error">mdi-delete</v-icon></v-btn
                          >
                        </div>
                      </div>
                    </v-expansion-panel-title>

                    <v-expansion-panel-text>
                      <v-alert
                        v-if="!isScripted"
                        type="info"
                        variant="tonal"
                        density="comfortable"
                        class="mb-2"
                      >
                        <strong>Adapter-driven</strong> mode: the environment
                        generates actions. The table below is stored in YAML as
                        documentation but is not executed.
                      </v-alert>
                      <v-alert
                        v-else
                        type="success"
                        variant="tonal"
                        density="comfortable"
                        class="mb-2"
                      >
                        <strong>Scripted</strong> mode: these actions will be
                        executed by the <code>scripted</code> environment.
                      </v-alert>

                      <div class="d-flex align-center justify-space-between">
                        <div class="text-subtitle-2">
                          Actions
                          <v-tooltip
                            text="For human actions fill Duration (s); for AI actions fill Latency (ms)."
                          >
                            <template #activator="{ props }"
                              ><v-icon size="16" v-bind="props" class="ml-1"
                                >mdi-help-circle-outline</v-icon
                              ></template
                            >
                          </v-tooltip>
                        </div>
                        <v-btn size="small" @click="addAction(t)"
                          ><v-icon start>mdi-plus</v-icon> Add Action</v-btn
                        >
                      </div>

                      <v-table density="compact" class="mt-2">
                        <thead>
                          <tr>
                            <th style="width: 180px">Name</th>
                            <th style="width: 160px">Actor</th>
                            <th style="width: 130px">Duration (s)</th>
                            <th style="width: 130px">Latency (ms)</th>
                            <th style="width: 130px">Correct?</th>
                            <th style="width: 140px"></th>
                          </tr>
                        </thead>

                        <tbody>
                          <!-- Helpful empty state -->
                          <tr v-if="t.actions.length === 0">
                            <td :colspan="6" class="pa-4">
                              <v-alert type="info" variant="tonal" class="mb-0">
                                No actions yet.
                                <v-btn
                                  size="small"
                                  class="ml-2"
                                  @click="addAction(t)"
                                >
                                  <v-icon start>mdi-plus</v-icon> Add Action
                                </v-btn>
                              </v-alert>
                            </td>
                          </tr>

                          <tr v-for="(a, ai) in t.actions" :key="a.id">
                            <td>
                              <v-text-field
                                v-model="a.name"
                                hide-details
                                density="compact"
                                :rules="[req]"
                                :disabled="!isScripted"
                              />
                            </td>

                            <td>
                              <v-select
                                :items="builder.agents.map((x) => x.id)"
                                v-model="a.actor"
                                hide-details
                                density="compact"
                                :rules="[req]"
                                :disabled="!isScripted"
                              />
                            </td>

                            <td>
                              <v-text-field
                                v-model.number="a.duration_s"
                                type="number"
                                hide-details="auto"
                                density="compact"
                                append-inner="s"
                                :disabled="!isScripted || !needsDuration(a)"
                                :rules="[
                                  (v) =>
                                    !isScripted || !needsDuration(a) || req(v),
                                  num,
                                ]"
                                :hint="
                                  needsDuration(a)
                                    ? isScripted
                                      ? 'Human step: seconds'
                                      : 'Disabled in adapter mode'
                                    : 'Disabled for AI'
                                "
                                persistent-hint
                              />
                            </td>

                            <td>
                              <v-text-field
                                v-model.number="a.latency_ms"
                                type="number"
                                hide-details="auto"
                                density="compact"
                                append-inner="ms"
                                :disabled="!isScripted || !needsLatency(a)"
                                :rules="[
                                  (v) =>
                                    !isScripted || !needsLatency(a) || req(v),
                                  num,
                                ]"
                                :hint="
                                  needsLatency(a)
                                    ? isScripted
                                      ? 'AI step: milliseconds'
                                      : 'Disabled in adapter mode'
                                    : 'Disabled for human'
                                "
                                persistent-hint
                              />
                            </td>

                            <td>
                              <v-select
                                :items="correctOptions"
                                v-model="a.correct"
                                hide-details="auto"
                                density="compact"
                                :disabled="!isScripted"
                                :hint="'Use Unknown if you don’t have a label.'"
                                persistent-hint
                              />
                            </td>

                            <td class="text-no-wrap">
                              <v-btn
                                icon
                                size="x-small"
                                @click="moveAction(t, ai, -1)"
                                :disabled="ai === 0"
                              >
                                <v-icon>mdi-arrow-up</v-icon>
                              </v-btn>
                              <v-btn
                                icon
                                size="x-small"
                                @click="moveAction(t, ai, 1)"
                                :disabled="ai === t.actions.length - 1"
                              >
                                <v-icon>mdi-arrow-down</v-icon>
                              </v-btn>
                              <v-btn
                                icon
                                size="x-small"
                                @click="removeAction(t, ai)"
                              >
                                <v-icon color="error">mdi-delete</v-icon>
                              </v-btn>
                            </td>
                          </tr>
                        </tbody>
                      </v-table>
                    </v-expansion-panel-text>
                  </v-expansion-panel>
                </v-expansion-panels>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <!-- ================== LIVE RUN ================== -->
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
                >
                  Export JSON
                </v-btn>
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

      <!-- ================== BROWSE ================== -->
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
                  <li v-for="(b, i) in browsedBullets" :key="i" v-html="b"></li>
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

      <!-- ================== VIZ ================== -->
      <v-window-item value="viz">
        <v-alert type="info" variant="tonal" class="mb-4">
          Hook your existing <code>SimulationMetricsChart</code> /
          <code>PlotChart</code> here if desired.
        </v-alert>
      </v-window-item>
    </v-window>

    <!-- SINGLE GLOBAL DIALOG -->
    <v-dialog
      v-model="yamlDlg"
      max-width="900"
      scrollable
      :retain-focus="false"
    >
      <v-card>
        <v-card-title class="py-3">Paste Config YAML</v-card-title>

        <v-card-text>
          <!-- persistent inline errors only -->
          <v-alert v-if="yamlErr" type="error" class="mb-2">{{
            yamlErr
          }}</v-alert>

          <v-textarea
            v-model="yamlText"
            class="code-textarea font-mono"
            :style="monoStyle"
            variant="outlined"
            rows="20"
            no-resize
            spellcheck="false"
            hint="Paste a full config (task_name, task_parameters, agent_definitions, profile_definitions, filename)."
            persistent-hint
          />
        </v-card-text>

        <v-card-actions class="py-2">
          <!-- LEFT: tertiary action + live stats -->
          <v-btn variant="text" @click="closeYaml" ref="yamlCloseBtn"
            >Close</v-btn
          >
          <div class="text-caption text-medium-emphasis ml-2 mr-auto">
            {{ yamlStats.lines }} lines · {{ yamlStats.chars }} chars
          </div>

          <!-- RIGHT: primary actions -->
          <v-btn variant="text" @click="validateYaml">Validate YAML</v-btn>
          <v-btn color="primary" :loading="building" @click="runFromYaml">
            <v-icon start>mdi-play</v-icon> Run with this YAML
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Global snackbar for transient success/info/errors -->
    <v-snackbar
      v-model="snack.show"
      :color="snack.color"
      location="bottom right"
      timeout="2500"
    >
      {{ snack.text }}
    </v-snackbar>
  </BaseLayout>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import BaseLayout from "@/components/BaseLayout.vue";
import { useRoute } from "vue-router";
import YAML from "js-yaml";
import { generateConfig, listConfigs } from "@/services/configurationService";
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

const envChoices = ["ct_scan", "overcooked", "scripted"]; // add more adapters here

const yamlDlg = ref(false);
const yamlText = ref("");
const yamlErr = ref("");
const snack = ref({ show: false, text: "", color: "success" });
const yamlBtn = ref(null);
const yamlCloseBtn = ref(null);

const monoStyle = {
  fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
};

const yamlStats = computed(() => {
  const s = yamlText.value || "";
  return { chars: s.length, lines: s.split(/\r?\n/).length };
});

function toast(text, color = "success") {
  snack.value = { show: true, text, color };
}

watch(yamlDlg, (open) => {
  if (!open) nextTick(() => yamlBtn.value?.focus?.());
});

function openYaml() {
  yamlErr.value = "";
  // Prefill from builder for quick edits/preview
  const obj = toConfigRequest(builder.value, mode.value);
  try {
    yamlText.value = YAML.dump(obj);
  } catch {
    yamlText.value = "";
  }
  yamlDlg.value = true;
}

function closeYaml() {
  yamlDlg.value = false; // Esc also closes
}

// ---------- tabs / routing ----------
const route = useRoute();
const tab = ref("live");

// ---------- sidebar state ----------
const running = ref(false);
const seed = ref("");
const configOptions = ref([]);
const selectedConfig = ref(null);

// ---------- results / browsing ----------
const result = ref(null);
const metricFiles = ref([]);
const browsed = ref(null);

// ---------- table headers ----------
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

// ---------- insights ----------
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

// ---------- validation helpers ----------
const req = (v) => (v !== null && v !== "" && v !== undefined) || "Required";
const num = (v) =>
  v === null || v === "" || !isNaN(Number(v)) || "Must be a number";

// ---------- execution mode ----------
const mode = ref("adapter"); // 'adapter' | 'scripted'
const isScripted = computed(() => mode.value === "scripted");

// ---------- actor helpers for conditional fields ----------
function actorTypeFor(actorId) {
  const ag = builder.value.agents.find((a) => a.id === actorId);
  return ag?.type || "human";
}
function needsDuration(a) {
  return actorTypeFor(a.actor) === "human";
}
function needsLatency(a) {
  return actorTypeFor(a.actor) === "ai";
}

// ---------- load selectable configs / runs ----------
async function refreshConfigs() {
  configOptions.value = await listConfigs();
  if (!selectedConfig.value && configOptions.value.length) {
    selectedConfig.value = configOptions.value[0];
  }
}
async function refreshRuns() {
  metricFiles.value = await listMetrics();
}

// ---------- run / load ----------
async function runSim() {
  if (!selectedConfig.value) return;
  running.value = true;
  try {
    result.value = await simulate(selectedConfig.value, seed.value);
    tab.value = "live";
    toast("Run complete", "success");
  } catch (e) {
    toast(e?.message || "Run failed", "error");
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

// ---------- BUILDER ----------
const builder = ref({
  name: "My Environment",
  version: "v1",
  environment: "ct_scan",
  seed: 123,
  metrics: { rt_max: 5.0, baseline_s: null },
  agents: [
    { id: "human1", name: "Radiologist", type: "human", profile: "default" },
    { id: "ai1", name: "AI Assistant", type: "ai", profile: "gpt" },
  ],
  tasks: [
    {
      id: "task-1",
      name: "Task 1",
      actions: [
        {
          id: "a1",
          name: "look",
          actor: "human1",
          duration_s: 0.8,
          correct: true,
        },
        {
          id: "a2",
          name: "suggest",
          actor: "ai1",
          latency_ms: 200,
          correct: true,
        },
      ],
    },
  ],
});

// tri-state for Correct?: Unknown / Correct / Incorrect
const correctOptions = [
  { title: "— Unknown", value: null },
  { title: "Correct", value: true },
  { title: "Incorrect", value: false },
];

const building = ref(false);
const buildMsg = ref("");
const buildErr = ref("");

function addTask() {
  builder.value.tasks.push({
    id: `task-${Date.now()}`,
    name: "New Task",
    actions: [],
  });
}
function removeTask(i) {
  builder.value.tasks.splice(i, 1);
}
function moveTask(i, dir) {
  const j = i + dir;
  if (j < 0 || j >= builder.value.tasks.length) return;
  const [row] = builder.value.tasks.splice(i, 1);
  builder.value.tasks.splice(j, 0, row);
}
function addAction(task) {
  task.actions.push({
    id: `act-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
    name: "action",
    actor: (builder.value.agents[0] && builder.value.agents[0].id) || "",
    duration_s: 0.5,
    latency_ms: null,
    correct: null,
  });
}
function removeAction(task, idx) {
  task.actions.splice(idx, 1);
}
function moveAction(task, i, dir) {
  const j = i + dir;
  if (j < 0 || j >= task.actions.length) return;
  const [row] = task.actions.splice(i, 1);
  task.actions.splice(j, 0, row);
}

async function generateAndRun() {
  buildErr.value = "";
  buildMsg.value = "";
  building.value = true;
  try {
    const payload = toConfigRequest(builder.value, mode.value);
    const gen = await generateConfig(payload);
    buildMsg.value = gen?.path
      ? `Config generated: ${gen.path}`
      : gen?.message || "Config generated";
    if (gen?.path && !configOptions.value.includes(gen.path)) {
      configOptions.value = [gen.path, ...configOptions.value];
    }
    selectedConfig.value = gen?.path || selectedConfig.value;
    toast(buildMsg.value, "success");

    await runSim();
    tab.value = "live";
  } catch (e) {
    buildErr.value = e?.response?.data?.detail || e?.message || String(e);
    toast(buildErr.value, "error");
  } finally {
    building.value = false;
    await refreshRuns();
  }
}

function toConfigRequest(b, mode) {
  const isScript = mode === "scripted";
  const envName = isScript ? "scripted" : b.environment || "ct_scan";
  const env_params = isScript ? { script: { tasks: b.tasks } } : {};

  const task_parameters = {
    environment: envName,
    env_params,
    dt: 0.1,
    rt_max: Number(b.metrics?.rt_max ?? 5),
    baseline_s: b.metrics?.baseline_s ?? null,
  };

  const seen = new Set();
  const profile_definitions = [];
  for (const a of b.agents || []) {
    const pid = a.profile || (a.type === "ai" ? "gpt" : "default");
    const key = `${pid}::${a.type}`;
    if (!seen.has(key)) {
      profile_definitions.push({ id: pid, type: a.type, parameters: {} });
      seen.add(key);
    }
  }

  const agent_definitions = (b.agents || []).map((a) => ({
    id: a.id,
    name: a.name || a.id,
    profile: a.profile || (a.type === "ai" ? "gpt" : "default"),
  }));

  const filename = `${(b.name || "task").replace(
    /[^A-Za-z0-9_.-]+/g,
    "_"
  )}_env.yaml`;

  return {
    task_name: b.name,
    task_description: b.version || null,
    task_parameters,
    agent_definitions,
    profile_definitions,
    filename,
  };
}

function ensureAgentNames(obj) {
  if (Array.isArray(obj?.agent_definitions)) {
    obj.agent_definitions = obj.agent_definitions.map((a) => ({
      ...a,
      name: a?.name || a?.id || "agent",
    }));
  }
  return obj;
}
function basicValidate(obj) {
  if (!obj?.task_parameters?.environment)
    throw new Error("Missing task_parameters.environment");
  if (
    !Array.isArray(obj?.agent_definitions) ||
    obj.agent_definitions.length === 0
  )
    throw new Error("Missing agent_definitions");
  for (const a of obj.agent_definitions) {
    if (!a.id) throw new Error("Each agent needs an id");
    if (!a.profile) throw new Error(`Agent "${a.id}" missing profile`);
  }
}
function validateYaml() {
  yamlErr.value = "";
  try {
    const obj = ensureAgentNames(
      YAML.load(yamlText.value || "", { schema: YAML.JSON_SCHEMA })
    );
    basicValidate(obj);
    toast("YAML looks valid ✅", "success");
  } catch (e) {
    yamlErr.value = e?.mark
      ? `Line ${e.mark.line + 1}, col ${e.mark.column + 1}: ${e.message}`
      : e?.message || String(e);
    toast("Validation failed", "error");
  }
}

async function runFromYaml() {
  yamlErr.value = "";
  buildErr.value = "";
  buildMsg.value = "";
  building.value = true;
  try {
    const obj = ensureAgentNames(
      YAML.load(yamlText.value || "", { schema: YAML.JSON_SCHEMA })
    );
    basicValidate(obj);

    const gen = await generateConfig(obj);
    buildMsg.value = gen?.path
      ? `Config generated: ${gen.path}`
      : gen?.message || "Config generated";
    if (gen?.path && !configOptions.value.includes(gen.path)) {
      configOptions.value = [gen.path, ...configOptions.value];
    }
    selectedConfig.value = gen?.path || selectedConfig.value;

    toast(buildMsg.value, "success");
    yamlDlg.value = false;

    await runSim();
    tab.value = "live";
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || String(e);
    yamlErr.value = msg;
    buildErr.value = msg;
    toast(msg, "error");
  } finally {
    building.value = false;
    await refreshRuns();
  }
}

// ---------- mount ----------
onMounted(async () => {
  await refreshConfigs();
  await refreshRuns();
  if (route.query.mode === "build") tab.value = "build";
});
</script>

<style scoped>
/* High-contrast monospace editor look without extra deps */
.code-textarea :deep(textarea) {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace !important;
  line-height: 1.35;
  tab-size: 2;
  min-height: 420px;
}
.code-textarea :deep(.v-field) {
  background: #0f172a; /* slate-900 */
  color: #e2e8f0; /* slate-200 */
}
.code-textarea :deep(.v-field__hint) {
  opacity: 0.8;
}
</style>
