<template>
  <BaseLayout>
    <v-container>
      <v-card class="mb-4">
        <v-card-title class="text-h6">Environment Builder (MVP)</v-card-title>
        <v-card-subtitle
          >Design → Generate Config → Run → View Insights</v-card-subtitle
        >
      </v-card>

      <!-- Stepper -->
      <v-stepper v-model="step" flat>
        <v-stepper-header>
          <v-stepper-item :value="1" title="Build" />
          <v-stepper-item :value="2" title="Agents" />
          <v-stepper-item :value="3" title="Preview & Run" />
        </v-stepper-header>

        <v-stepper-window>
          <!-- STEP 1: BUILD -->
          <v-stepper-window-item :value="1">
            <v-row>
              <v-col cols="12" md="8">
                <v-card class="pa-3">
                  <v-text-field
                    v-model="env.name"
                    label="Environment Name"
                    density="comfortable"
                  />
                  <v-text-field
                    v-model="env.version"
                    label="Version"
                    density="comfortable"
                  />

                  <v-divider class="my-3" />

                  <div class="d-flex align-center justify-space-between">
                    <div class="text-subtitle-2">Tasks</div>
                    <v-btn size="small" @click="addTask"
                      ><v-icon start>mdi-plus</v-icon>Add Task</v-btn
                    >
                  </div>

                  <v-expansion-panels multiple class="mt-2">
                    <v-expansion-panel
                      v-for="(task, ti) in env.tasks"
                      :key="task.id"
                    >
                      <v-expansion-panel-title>
                        <div
                          class="d-flex align-center w-100 justify-space-between"
                        >
                          <div>
                            <v-text-field
                              v-model="task.name"
                              label="Task Name"
                              hide-details
                              class="ma-0 pa-0"
                              density="compact"
                            />
                          </div>
                          <div>
                            <v-btn
                              icon
                              size="small"
                              @click.stop="moveTask(ti, -1)"
                              :disabled="ti === 0"
                            >
                              <v-icon>mdi-arrow-up</v-icon>
                            </v-btn>
                            <v-btn
                              icon
                              size="small"
                              @click.stop="moveTask(ti, 1)"
                              :disabled="ti === env.tasks.length - 1"
                            >
                              <v-icon>mdi-arrow-down</v-icon>
                            </v-btn>
                            <v-btn
                              icon
                              size="small"
                              @click.stop="removeTask(ti)"
                            >
                              <v-icon color="error">mdi-delete</v-icon>
                            </v-btn>
                          </div>
                        </div>
                      </v-expansion-panel-title>

                      <v-expansion-panel-text>
                        <div class="d-flex align-center justify-space-between">
                          <div class="text-subtitle-2">Actions</div>
                          <v-btn size="small" @click="addAction(task)">
                            <v-icon start>mdi-plus</v-icon> Add Action
                          </v-btn>
                        </div>

                        <v-table density="compact" class="mt-2">
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>Actor</th>
                              <th>Duration (s)</th>
                              <th>Latency (ms)</th>
                              <th>Correct?</th>
                              <th></th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr v-for="(act, ai) in task.actions" :key="act.id">
                              <td>
                                <v-text-field
                                  v-model="act.name"
                                  hide-details
                                  density="compact"
                                />
                              </td>
                              <td>
                                <v-select
                                  :items="agentOptions"
                                  v-model="act.actor"
                                  hide-details
                                  density="compact"
                                />
                              </td>
                              <td>
                                <v-text-field
                                  v-model.number="act.duration_s"
                                  type="number"
                                  hide-details
                                  density="compact"
                                />
                              </td>
                              <td>
                                <v-text-field
                                  v-model.number="act.latency_ms"
                                  type="number"
                                  hide-details
                                  density="compact"
                                />
                              </td>
                              <td>
                                <v-select
                                  :items="boolItems"
                                  v-model="act.correct"
                                  hide-details
                                  density="compact"
                                />
                              </td>
                              <td class="text-no-wrap">
                                <v-btn
                                  icon
                                  size="x-small"
                                  @click="moveAction(task, ai, -1)"
                                  :disabled="ai === 0"
                                  ><v-icon>mdi-arrow-up</v-icon></v-btn
                                >
                                <v-btn
                                  icon
                                  size="x-small"
                                  @click="moveAction(task, ai, 1)"
                                  :disabled="ai === task.actions.length - 1"
                                  ><v-icon>mdi-arrow-down</v-icon></v-btn
                                >
                                <v-btn
                                  icon
                                  size="x-small"
                                  @click="removeAction(task, ai)"
                                  ><v-icon color="error"
                                    >mdi-delete</v-icon
                                  ></v-btn
                                >
                              </td>
                            </tr>
                          </tbody>
                        </v-table>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card>
              </v-col>

              <v-col cols="12" md="4">
                <v-card class="pa-3">
                  <div class="text-subtitle-2 mb-2">Metrics Parameters</div>
                  <v-text-field
                    v-model.number="env.metrics.rt_max"
                    type="number"
                    label="rt_max (s)"
                    density="comfortable"
                  />
                  <v-text-field
                    v-model.number="env.metrics.baseline_s"
                    type="number"
                    label="baseline_s (s, optional)"
                    density="comfortable"
                  />
                  <v-divider class="my-3" />
                  <div class="text-subtitle-2">Tips</div>
                  <ul class="text-caption">
                    <li>
                      Use <em>duration_s</em> for human actions;
                      <em>latency_ms</em> for AI.
                    </li>
                    <li>
                      Set <em>correct</em> to feed Trust/Adaptability (Tr, A).
                    </li>
                  </ul>
                </v-card>
              </v-col>
            </v-row>
          </v-stepper-window-item>

          <!-- STEP 2: AGENTS -->
          <v-stepper-window-item :value="2">
            <v-row>
              <v-col cols="12" md="8">
                <v-card class="pa-3">
                  <div class="d-flex align-center justify-space-between">
                    <div class="text-subtitle-2">Agents</div>
                    <v-btn size="small" @click="addAgent"
                      ><v-icon start>mdi-plus</v-icon>Add Agent</v-btn
                    >
                  </div>

                  <v-table density="compact" class="mt-2">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Type</th>
                        <th>Profile</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(ag, i) in env.agents" :key="ag.id">
                        <td>
                          <v-text-field
                            v-model="ag.id"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-select
                            :items="['human', 'ai']"
                            v-model="ag.type"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-text-field
                            v-model="ag.profile"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-btn icon size="x-small" @click="removeAgent(i)"
                            ><v-icon color="error">mdi-delete</v-icon></v-btn
                          >
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-card>
              </v-col>
            </v-row>
          </v-stepper-window-item>

          <!-- STEP 3: PREVIEW & RUN -->
          <v-stepper-window-item :value="3">
            <v-row>
              <v-col cols="12" md="8">
                <v-card class="pa-3">
                  <div class="text-subtitle-2 mb-2">
                    Preview (JSON sent to backend)
                  </div>
                  <pre
                    class="pa-2 bg-grey-lighten-4"
                    style="max-height: 300px; overflow: auto"
                    >{{ pretty(env) }}</pre
                  >
                  <v-divider class="my-2" />
                  <v-btn
                    color="primary"
                    :loading="busy"
                    @click="onGenerateAndRun"
                  >
                    <v-icon start>mdi-play</v-icon> Generate Config & Run
                  </v-btn>
                  <v-alert v-if="error" type="error" class="mt-3">{{
                    error
                  }}</v-alert>
                  <v-alert v-if="success" type="success" class="mt-3">{{
                    success
                  }}</v-alert>
                </v-card>
              </v-col>

              <v-col cols="12" md="4" v-if="artifact">
                <!-- Insights after run (Core v1) -->
                <CoreMetricsSummary
                  :summary="artifact.metrics"
                  :params="artifact.params"
                />
              </v-col>
            </v-row>
          </v-stepper-window-item>
        </v-stepper-window>

        <v-stepper-actions>
          <v-btn variant="tonal" @click="prev" :disabled="step === 1"
            >Back</v-btn
          >
          <v-spacer />
          <v-btn color="primary" @click="next" :disabled="step === 3"
            >Next</v-btn
          >
        </v-stepper-actions>
      </v-stepper>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import CoreMetricsSummary from "@/components/CoreMetricsSummary.vue";
import { generateEnvConfig, runSimulation } from "@/services/envBuilderService";
import { computeCoreV1 } from "@/services/coreMetricsService";

export default {
  name: "EnvBuilderPage",
  components: { BaseLayout, CoreMetricsSummary },
  data() {
    return {
      step: 1,
      env: {
        name: "My Environment",
        version: "v1",
        metrics: { rt_max: 5.0, baseline_s: null },
        agents: [
          { id: "human1", type: "human", profile: "default" },
          { id: "ai1", type: "ai", profile: "gpt" },
        ],
        tasks: [],
      },
      boolItems: [true, false],
      busy: false,
      error: "",
      success: "",
      artifact: null,
    };
  },
  computed: {
    agentOptions() {
      return this.env.agents.map((a) => a.id);
    },
  },
  methods: {
    // stepper
    next() {
      this.step = Math.min(3, this.step + 1);
    },
    prev() {
      this.step = Math.max(1, this.step - 1);
    },

    // helpers
    pretty(obj) {
      return JSON.stringify(obj, null, 2);
    },

    // tasks & actions
    addTask() {
      const id = `task-${Date.now()}`;
      this.env.tasks.push({ id, name: "New Task", actions: [] });
    },
    removeTask(i) {
      this.env.tasks.splice(i, 1);
    },
    moveTask(i, dir) {
      const j = i + dir;
      if (j < 0 || j >= this.env.tasks.length) return;
      const [x] = this.env.tasks.splice(i, 1);
      this.env.tasks.splice(j, 0, x);
    },

    addAction(task) {
      task.actions.push({
        id: `act-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
        name: "action",
        actor: this.agentOptions[0] || "",
        duration_s: 0.5,
        latency_ms: null,
        correct: true,
      });
    },
    removeAction(task, idx) {
      task.actions.splice(idx, 1);
    },
    moveAction(task, i, dir) {
      const j = i + dir;
      if (j < 0 || j >= task.actions.length) return;
      const [x] = task.actions.splice(i, 1);
      task.actions.splice(j, 0, x);
    },

    // generate & run
    async onGenerateAndRun() {
      this.error = "";
      this.success = "";
      this.busy = true;
      try {
        // send the builder state as-is; backend turns it into YAML/config
        const gen = await generateEnvConfig({ env: this.env });
        this.success = `Config generated: ${gen.path}`;
        const run = await runSimulation(gen.path);
        // compute Core v1 for quick insights
        const art = await computeCoreV1(run.run_id, {
          rt_max: this.env.metrics.rt_max,
          baseline_s: this.env.metrics.baseline_s,
        });
        this.artifact = art;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || String(e);
      } finally {
        this.busy = false;
      }
    },
  },
};
</script>

<style scoped>
pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", monospace;
}
</style>
