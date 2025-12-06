<template>
  <BaseLayout>
    <v-container>
      <v-card class="mb-4">
        <v-card-title class="text-h6">HAIC Simulation Builder</v-card-title>
        <v-card-subtitle
          >Create and run Human-AI Collaboration simulations</v-card-subtitle
        >
      </v-card>

      <!-- Main tabs for different simulation types -->
      <v-tabs v-model="activeTab" bg-color="primary">
        <v-tab value="scripted">Scripted Simulation</v-tab>
        <v-tab value="dataset">Dataset A/B Testing</v-tab>
        <v-tab value="env-builder">Environment Builder</v-tab>
      </v-tabs>

      <v-tabs-window v-model="activeTab">
        <!-- SCRIPTED SIMULATION TAB -->
        <v-tabs-window-item value="scripted">
          <v-stepper v-model="scriptedStep" flat class="mt-4">
            <v-stepper-header>
              <v-stepper-item :value="1" title="Config" />
              <v-stepper-item :value="2" title="Script" />
              <v-stepper-item :value="3" title="Run" />
            </v-stepper-header>

            <v-stepper-window>
              <!-- Step 1: Config -->
              <v-stepper-window-item :value="1">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-card class="pa-3">
                      <v-card-title>Environment</v-card-title>
                      <v-text-field
                        v-model="haicConfig.sim_id"
                        label="Simulation ID"
                        density="comfortable"
                      />
                      <v-text-field
                        v-model="haicConfig.environment.id"
                        label="Environment ID"
                        density="comfortable"
                      />
                      <v-text-field
                        v-model="haicConfig.environment.attributes.task"
                        label="Task"
                        density="comfortable"
                      />
                      <v-text-field
                        v-model="haicConfig.environment.attributes.domain"
                        label="Domain"
                        density="comfortable"
                      />
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-card class="pa-3">
                      <v-card-title>Agents & Objects</v-card-title>
                      <div class="d-flex justify-space-between mb-2">
                        <span class="text-subtitle-2">Agents</span>
                        <v-btn size="small" @click="addHAICAgent">
                          <v-icon start>mdi-plus</v-icon>Add Agent
                        </v-btn>
                      </div>
                      <v-table density="compact">
                        <thead>
                          <tr>
                            <th>ID</th>
                            <th>Model</th>
                            <th>Affordances</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(agent, i) in haicConfig.agents"
                            :key="agent.id"
                          >
                            <td>
                              <v-text-field
                                v-model="agent.id"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-select
                                :items="['human', 'ai']"
                                v-model="agent.model"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="agent.affordances"
                                placeholder="view,classify"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-btn
                                icon
                                size="x-small"
                                @click="removeHAICAgent(i)"
                              >
                                <v-icon color="error">mdi-delete</v-icon>
                              </v-btn>
                            </td>
                          </tr>
                        </tbody>
                      </v-table>

                      <div class="d-flex justify-space-between mb-2 mt-4">
                        <span class="text-subtitle-2">Objects</span>
                        <v-btn size="small" @click="addHAICObject">
                          <v-icon start>mdi-plus</v-icon>Add Object
                        </v-btn>
                      </div>
                      <v-table density="compact">
                        <thead>
                          <tr>
                            <th>ID</th>
                            <th>Affordances</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr
                            v-for="(obj, i) in haicConfig.objects"
                            :key="obj.id"
                          >
                            <td>
                              <v-text-field
                                v-model="obj.id"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="obj.affordances"
                                placeholder="view,classify"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-btn
                                icon
                                size="x-small"
                                @click="removeHAICObject(i)"
                              >
                                <v-icon color="error">mdi-delete</v-icon>
                              </v-btn>
                            </td>
                          </tr>
                        </tbody>
                      </v-table>
                    </v-card>
                  </v-col>
                </v-row>
              </v-stepper-window-item>

              <!-- Step 2: Script -->
              <v-stepper-window-item :value="2">
                <v-card class="pa-3">
                  <v-card-title>Simulation Script</v-card-title>
                  <div class="d-flex justify-space-between mb-2">
                    <span class="text-subtitle-2">Steps</span>
                    <v-btn size="small" @click="addHAICStep">
                      <v-icon start>mdi-plus</v-icon>Add Step
                    </v-btn>
                  </div>
                  <v-table density="compact">
                    <thead>
                      <tr>
                        <th>t</th>
                        <th>Agent</th>
                        <th>Action</th>
                        <th>Object</th>
                        <th>Effect (JSON)</th>
                        <th>Latency (ms)</th>
                        <th>Correct</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(step, i) in haicConfig.script" :key="i">
                        <td>
                          <v-text-field
                            v-model.number="step.t"
                            type="number"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-select
                            :items="haicAgentIds"
                            v-model="step.agent"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-text-field
                            v-model="step.action"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-select
                            :items="haicObjectIds"
                            v-model="step.object"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-text-field
                            v-model="step.effect_json"
                            placeholder='{"ai_label":"benign"}'
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-text-field
                            v-model.number="step.latency_ms"
                            type="number"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-checkbox
                            v-model="step.correct"
                            hide-details
                            density="compact"
                          />
                        </td>
                        <td>
                          <v-btn icon size="x-small" @click="removeHAICStep(i)">
                            <v-icon color="error">mdi-delete</v-icon>
                          </v-btn>
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-card>
              </v-stepper-window-item>

              <!-- Step 3: Run -->
              <v-stepper-window-item :value="3">
                <v-row>
                  <v-col cols="12" md="8">
                    <v-card class="pa-3">
                      <v-card-title>Preview & Run</v-card-title>
                      <div class="text-subtitle-2 mb-2">Config Preview</div>
                      <pre
                        class="pa-2 bg-grey-lighten-4"
                        style="max-height: 300px; overflow: auto"
                        >{{ prettyHAICConfig }}
                      </pre>
                      <v-divider class="my-2" />
                      <v-btn
                        color="primary"
                        :loading="busy"
                        @click="runHAICSimulation"
                      >
                        <v-icon start>mdi-play</v-icon> Run Simulation
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
                    <CoreMetricsSummary
                      :summary="artifact.metrics"
                      :params="artifact.params"
                    />
                  </v-col>
                </v-row>
              </v-stepper-window-item>
            </v-stepper-window>

            <v-stepper-actions>
              <v-btn
                variant="tonal"
                @click="prevScripted"
                :disabled="scriptedStep === 1"
                >Back</v-btn
              >
              <v-spacer />
              <v-btn
                color="primary"
                @click="nextScripted"
                :disabled="scriptedStep === 3"
                >Next</v-btn
              >
            </v-stepper-actions>
          </v-stepper>
        </v-tabs-window-item>

        <!-- DATASET A/B TESTING TAB -->
        <v-tabs-window-item value="dataset">
          <v-card class="pa-3 mt-4">
            <v-card-title>Dataset A/B Testing</v-card-title>
            <v-card-subtitle
              >Compare Baseline vs L2D policies on CSV datasets</v-card-subtitle
            >

            <v-row>
              <v-col cols="12" md="6">
                <v-file-input
                  v-model="datasetFile"
                  label="Select CSV Dataset"
                  accept=".csv"
                  show-size
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="experimentMode"
                  :items="['baseline', 'l2d']"
                  label="Experiment Mode"
                  density="comfortable"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="threshold"
                  type="number"
                  label="Baseline Threshold"
                  step="0.01"
                  min="0"
                  max="1"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="tau"
                  type="number"
                  label="L2D τ (Uncertainty Band)"
                  step="0.01"
                  min="0.5"
                  max="1"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model.number="humanAccuracy"
                  type="number"
                  label="Human Accuracy"
                  step="0.01"
                  min="0"
                  max="1"
                  density="comfortable"
                />
              </v-col>
            </v-row>

            <v-btn
              color="primary"
              :loading="busy"
              @click="runDatasetExperiment"
              class="mt-3"
            >
              <v-icon start>mdi-flask</v-icon> Run A/B Experiment
            </v-btn>

            <v-alert v-if="error" type="error" class="mt-3">{{
              error
            }}</v-alert>
            <v-alert v-if="success" type="success" class="mt-3">{{
              success
            }}</v-alert>
          </v-card>
        </v-tabs-window-item>

        <!-- ENVIRONMENT BUILDER TAB (original) -->
        <v-tabs-window-item value="env-builder">
          <!-- Stepper -->
          <v-stepper v-model="step" flat class="mt-4">
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
                            <div
                              class="d-flex align-center justify-space-between"
                            >
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
                                <tr
                                  v-for="(act, ai) in task.actions"
                                  :key="act.id"
                                >
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
                          Set <em>correct</em> to feed Trust/Adaptability (Tr,
                          A).
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
                                ><v-icon color="error"
                                  >mdi-delete</v-icon
                                ></v-btn
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
        </v-tabs-window-item>
      </v-tabs-window>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import CoreMetricsSummary from "@/components/CoreMetricsSummary.vue";
import {
  generateEnvConfig,
  runSimulation,
  runHAICSimMVPConfig,
  runDatasetExperiment,
} from "@/services/envBuilderService";
import { computeCoreV1 } from "@/services/coreMetricsService";

export default {
  name: "EnvBuilderPage",
  components: { BaseLayout, CoreMetricsSummary },
  data() {
    return {
      activeTab: "scripted",
      scriptedStep: 1,
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
      // HAIC Sim MVP data
      haicConfig: {
        sim_id: "ct_demo",
        environment: {
          id: "CT_Diagnosis",
          class: "base.Environment",
          attributes: { task: "classification", domain: "medical" },
        },
        agents: [
          {
            id: "A1",
            class: "user_plugins.medical.Radiologist",
            model: "human",
            attributes: { viewed_cases: [] },
            affordances: ["view", "classify"],
          },
          {
            id: "A2",
            class: "base.Agent",
            model: "ai",
            attributes: {},
            affordances: ["classify"],
          },
        ],
        objects: [
          {
            id: "O1",
            class: "user_plugins.medical.CTImage",
            attributes: { type: "CT" },
            affordances: ["view", "classify"],
          },
        ],
        script: [],
      },
      // Dataset experiment data
      datasetFile: null,
      experimentMode: "baseline",
      threshold: 0.5,
      tau: 0.7,
      humanAccuracy: 0.9,
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
    haicAgentIds() {
      return this.haicConfig.agents.map((a) => a.id);
    },
    haicObjectIds() {
      return this.haicConfig.objects.map((o) => o.id);
    },
    prettyHAICConfig() {
      return JSON.stringify(this.haicConfig, null, 2);
    },
  },
  methods: {
    // Main stepper
    next() {
      this.step = Math.min(3, this.step + 1);
    },
    prev() {
      this.step = Math.max(1, this.step - 1);
    },

    // Scripted stepper
    nextScripted() {
      this.scriptedStep = Math.min(3, this.scriptedStep + 1);
    },
    prevScripted() {
      this.scriptedStep = Math.max(1, this.scriptedStep - 1);
    },

    // helpers
    pretty(obj) {
      return JSON.stringify(obj, null, 2);
    },

    // Environment builder methods
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
    addAgent() {
      this.env.agents.push({
        id: `agent${this.env.agents.length + 1}`,
        type: "human",
        profile: "default",
      });
    },
    removeAgent(i) {
      this.env.agents.splice(i, 1);
    },

    // HAIC methods
    addHAICAgent() {
      const id = `A${this.haicConfig.agents.length + 1}`;
      this.haicConfig.agents.push({
        id,
        class: "base.Agent",
        model: "human",
        attributes: {},
        affordances: ["view", "classify"],
      });
    },
    removeHAICAgent(i) {
      this.haicConfig.agents.splice(i, 1);
    },
    addHAICObject() {
      const id = `O${this.haicConfig.objects.length + 1}`;
      this.haicConfig.objects.push({
        id,
        class: "base.Object",
        attributes: {},
        affordances: ["view", "classify"],
      });
    },
    removeHAICObject(i) {
      this.haicConfig.objects.splice(i, 1);
    },
    addHAICStep() {
      this.haicConfig.script.push({
        t: this.haicConfig.script.length + 1,
        agent: this.haicAgentIds[0] || "",
        action: "view",
        object: this.haicObjectIds[0] || "",
        effect_json: "{}",
        latency_ms: 1000,
        correct: null,
      });
    },
    removeHAICStep(i) {
      this.haicConfig.script.splice(i, 1);
    },

    // Run methods
    async onGenerateAndRun() {
      this.error = "";
      this.success = "";
      this.busy = true;
      try {
        const gen = await generateEnvConfig({ env: this.env });
        this.success = `Config generated: ${gen.path}`;
        const run = await runSimulation(gen.path);
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

    async runHAICSimulation() {
      this.error = "";
      this.success = "";
      this.busy = true;
      try {
        const result = await runHAICSimMVPConfig(this.haicConfig);
        this.success = `Simulation completed. Log: ${
          result.log_path || "generated"
        }`;
        this.artifact = result;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || String(e);
      } finally {
        this.busy = false;
      }
    },

    async runDatasetExperiment() {
      this.error = "";
      this.success = "";
      this.busy = true;
      try {
        if (!this.datasetFile) {
          throw new Error("Please select a CSV dataset file");
        }
        const result = await runDatasetExperiment(
          this.datasetFile.name,
          this.experimentMode
        );
        this.success = result.message || "Dataset experiment completed";
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
