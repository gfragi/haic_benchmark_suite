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
      <v-tabs v-model="activeTab" bg-color="primary" class="mb-4">
        <v-tab value="scripted">
          <v-icon start>mdi-script-text</v-icon>
          Scripted HAIC Simulation
        </v-tab>
        <v-tab value="dataset">
          <v-icon start>mdi-flask</v-icon>
          Dataset A/B Testing
        </v-tab>
        <v-tab value="env-builder">
          <v-icon start>mdi-cog</v-icon>
          YAML Environment Builder
        </v-tab>
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
          <!-- Instructions for Environment Builder -->
          <v-alert type="info" variant="tonal" class="mb-4">
            <strong>YAML Environment Builder:</strong> Design high-level
            environments with tasks and agents. Generated configs are saved and
            can be run in the <strong>Simulator</strong> tab.
          </v-alert>

          <!-- Stepper -->
          <v-stepper v-model="step" flat class="mt-4">
            <v-stepper-header>
              <v-stepper-item :value="1" title="Environment & Tasks" />
              <v-stepper-item :value="2" title="Agents" />
              <v-stepper-item :value="3" title="Objects" />
              <v-stepper-item :value="4" title="Simulation Script" />
              <v-stepper-item :value="5" title="Run & Evaluate" />
            </v-stepper-header>

            <v-stepper-window>
              <!-- STEP 1: BUILD -->
              <v-stepper-window-item :value="1">
                <v-row>
                  <v-col cols="12" md="8">
                    <v-card class="pa-3">
                      <!-- Load Environment Section -->
                      <div class="mb-4">
                        <div class="text-subtitle-2 mb-2">Load Environment</div>
                        <v-row>
                          <v-col cols="12" md="4">
                            <v-file-input
                              v-model="envFile"
                              label="Load YAML/JSON File"
                              accept=".yaml,.yml,.json"
                              show-size
                              density="comfortable"
                              @change="loadEnvFromFile"
                            />
                          </v-col>
                          <v-col cols="12" md="4">
                            <v-select
                              v-model="selectedTemplate"
                              :items="envTemplates"
                              label="Load Template"
                              item-title="name"
                              item-value="key"
                              clearable
                              density="comfortable"
                              @update:model-value="loadTemplate"
                            />
                          </v-col>
                          <v-col cols="12" md="4">
                            <v-select
                              v-model="selectedPilot"
                              :items="haicPilots"
                              label="Load HAIC Pilot"
                              item-title="display_name"
                              item-value="name"
                              clearable
                              density="comfortable"
                              @update:model-value="loadHAICPilot"
                            >
                              <template v-slot:item="{ props, item }">
                                <v-list-item v-bind="props">
                                  <template v-slot:prepend>
                                    <v-chip
                                      size="small"
                                      :color="getDomainColor(item.raw.domain)"
                                    >
                                      {{ item.raw.domain }}
                                    </v-chip>
                                  </template>
                                  <v-list-item-title>{{
                                    item.title
                                  }}</v-list-item-title>
                                  <v-list-item-subtitle>{{
                                    item.raw.sim_id
                                  }}</v-list-item-subtitle>
                                </v-list-item>
                              </template>
                            </v-select>
                          </v-col>
                        </v-row>

                        <v-textarea
                          v-model="envJson"
                          label="Or paste JSON/YAML content"
                          placeholder='{"name": "My Environment", "version": "v1", "agents": [...], "tasks": [...]}'
                          rows="3"
                          density="comfortable"
                          class="mt-2"
                        />
                        <div class="d-flex gap-2 mt-2">
                          <v-btn size="small" @click="parseEnvJson">
                            <v-icon start>mdi-code-json</v-icon>
                            Parse JSON
                          </v-btn>
                          <v-btn size="small" @click="parseEnvYaml">
                            <v-icon start>mdi-file-code</v-icon>
                            Parse YAML
                          </v-btn>
                        </div>
                      </div>

                      <v-divider class="my-3" />

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

                      <div
                        v-if="env.tasks.length === 0"
                        class="text-center py-8"
                      >
                        <v-icon size="64" color="grey-lighten-1" class="mb-4"
                          >mdi-package-variant-closed</v-icon
                        >
                        <div class="text-h6 text-grey mb-2">No Tasks Yet</div>
                        <div class="text-body-2 text-grey mb-4">
                          Add your first task to get started
                        </div>
                        <v-btn color="primary" @click="addTask">
                          <v-icon start>mdi-plus</v-icon>
                          Add First Task
                        </v-btn>
                      </div>

                      <div v-else>
                        <v-expansion-panels
                          multiple
                          class="mt-2"
                          variant="accordion"
                        >
                          <v-expansion-panel
                            v-for="(task, ti) in env.tasks"
                            :key="task.id"
                            class="mb-2"
                          >
                            <v-expansion-panel-title class="px-4 py-3">
                              <div class="d-flex align-center w-100">
                                <v-icon class="mr-3" color="primary"
                                  >mdi-playlist-check</v-icon
                                >
                                <div class="flex-grow-1">
                                  <v-text-field
                                    v-model="task.name"
                                    label="Task Name"
                                    hide-details
                                    density="compact"
                                    class="mb-0"
                                    style="font-size: 1.1em; font-weight: 500"
                                  />
                                  <div
                                    class="text-caption text-medium-emphasis"
                                  >
                                    {{ task.actions.length }} action{{
                                      task.actions.length !== 1 ? "s" : ""
                                    }}
                                  </div>
                                </div>
                                <div class="d-flex gap-1 ml-3">
                                  <v-btn
                                    icon
                                    size="small"
                                    variant="text"
                                    @click.stop="moveTask(ti, -1)"
                                    :disabled="ti === 0"
                                    color="primary"
                                  >
                                    <v-icon size="18">mdi-arrow-up</v-icon>
                                  </v-btn>
                                  <v-btn
                                    icon
                                    size="small"
                                    variant="text"
                                    @click.stop="moveTask(ti, 1)"
                                    :disabled="ti === env.tasks.length - 1"
                                    color="primary"
                                  >
                                    <v-icon size="18">mdi-arrow-down</v-icon>
                                  </v-btn>
                                  <v-btn
                                    icon
                                    size="small"
                                    variant="text"
                                    @click.stop="removeTask(ti)"
                                    color="error"
                                  >
                                    <v-icon size="18">mdi-delete</v-icon>
                                  </v-btn>
                                </div>
                              </div>
                            </v-expansion-panel-title>

                            <v-expansion-panel-text class="px-4 py-3">
                              <!-- Actions Header -->
                              <div
                                class="d-flex align-center justify-space-between mb-4"
                              >
                                <div class="d-flex align-center">
                                  <v-icon class="mr-2" color="secondary"
                                    >mdi-gesture-tap</v-icon
                                  >
                                  <span
                                    class="text-subtitle-1 font-weight-medium"
                                    >Actions</span
                                  >
                                  <v-chip
                                    size="small"
                                    class="ml-2"
                                    color="secondary"
                                    variant="outlined"
                                  >
                                    {{ task.actions.length }}
                                  </v-chip>
                                </div>
                                <v-btn
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                  @click="addAction(task)"
                                >
                                  <v-icon start>mdi-plus</v-icon> Add Action
                                </v-btn>
                              </div>

                              <!-- Actions Table -->
                              <div
                                v-if="task.actions.length === 0"
                                class="text-center py-6"
                              >
                                <v-icon
                                  size="48"
                                  color="grey-lighten-1"
                                  class="mb-3"
                                  >mdi-gesture-tap</v-icon
                                >
                                <div class="text-body-1 text-grey mb-2">
                                  No Actions Yet
                                </div>
                                <div class="text-caption text-grey">
                                  Click "Add Action" to get started
                                </div>
                              </div>

                              <div v-else class="actions-table-container">
                                <v-table
                                  density="comfortable"
                                  class="actions-table"
                                >
                                  <thead>
                                    <tr class="bg-grey-lighten-4">
                                      <th class="text-left font-weight-medium">
                                        Name
                                      </th>
                                      <th class="text-left font-weight-medium">
                                        Actor
                                      </th>
                                      <th class="text-left font-weight-medium">
                                        Duration (s)
                                      </th>
                                      <th class="text-left font-weight-medium">
                                        Latency (ms)
                                      </th>
                                      <th class="text-left font-weight-medium">
                                        Correct?
                                      </th>
                                      <th
                                        class="text-center font-weight-medium"
                                      >
                                        Actions
                                      </th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    <tr
                                      v-for="(act, ai) in task.actions"
                                      :key="act.id"
                                      class="action-row"
                                    >
                                      <td class="action-name-cell">
                                        <v-text-field
                                          v-model="act.name"
                                          placeholder="Action name"
                                          hide-details
                                          density="compact"
                                          variant="outlined"
                                          class="action-input"
                                        />
                                      </td>
                                      <td class="action-actor-cell">
                                        <v-select
                                          :items="agentOptions"
                                          v-model="act.actor"
                                          placeholder="Select actor"
                                          hide-details
                                          density="compact"
                                          variant="outlined"
                                          class="action-input"
                                        />
                                      </td>
                                      <td class="action-duration-cell">
                                        <v-text-field
                                          v-model.number="act.duration_s"
                                          type="number"
                                          step="0.1"
                                          min="0"
                                          placeholder="0.0"
                                          hide-details
                                          density="compact"
                                          variant="outlined"
                                          class="action-input"
                                        />
                                      </td>
                                      <td class="action-latency-cell">
                                        <v-text-field
                                          v-model.number="act.latency_ms"
                                          type="number"
                                          step="100"
                                          min="0"
                                          placeholder="0"
                                          hide-details
                                          density="compact"
                                          variant="outlined"
                                          class="action-input"
                                        />
                                      </td>
                                      <td class="action-correct-cell">
                                        <v-select
                                          :items="boolItems"
                                          v-model="act.correct"
                                          placeholder="Select"
                                          hide-details
                                          density="compact"
                                          variant="outlined"
                                          class="action-input"
                                          :item-title="
                                            (item) => (item ? 'Yes' : 'No')
                                          "
                                          :item-value="(item) => item"
                                        >
                                          <template v-slot:selection="{ item }">
                                            <v-chip
                                              :color="
                                                item.value ? 'success' : 'error'
                                              "
                                              size="small"
                                              variant="flat"
                                            >
                                              {{ item.value ? "Yes" : "No" }}
                                            </v-chip>
                                          </template>
                                        </v-select>
                                      </td>
                                      <td
                                        class="action-controls-cell text-center"
                                      >
                                        <div
                                          class="d-flex justify-center gap-1"
                                        >
                                          <v-btn
                                            icon
                                            size="small"
                                            variant="text"
                                            @click="moveAction(task, ai, -1)"
                                            :disabled="ai === 0"
                                            color="primary"
                                          >
                                            <v-icon size="16"
                                              >mdi-chevron-up</v-icon
                                            >
                                          </v-btn>
                                          <v-btn
                                            icon
                                            size="small"
                                            variant="text"
                                            @click="moveAction(task, ai, 1)"
                                            :disabled="
                                              ai === task.actions.length - 1
                                            "
                                            color="primary"
                                          >
                                            <v-icon size="16"
                                              >mdi-chevron-down</v-icon
                                            >
                                          </v-btn>
                                          <v-btn
                                            icon
                                            size="small"
                                            variant="text"
                                            @click="removeAction(task, ai)"
                                            color="error"
                                          >
                                            <v-icon size="16"
                                              >mdi-delete</v-icon
                                            >
                                          </v-btn>
                                        </div>
                                      </td>
                                    </tr>
                                  </tbody>
                                </v-table>
                              </div>
                            </v-expansion-panel-text>
                          </v-expansion-panel>
                        </v-expansion-panels>
                      </div>
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
                            <th>Affordances</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(ag, i) in env.agents" :key="ag.id">
                            <td>
                              <v-text-field
                                v-model="ag.id"
                                placeholder="agent_id"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-select
                                :items="['human', 'ai', 'system']"
                                v-model="ag.type"
                                placeholder="Select type"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="ag.profile"
                                placeholder="default"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="ag.affordances"
                                placeholder="view,classify"
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

              <!-- STEP 3: OBJECTS -->
              <v-stepper-window-item :value="3">
                <v-row>
                  <v-col cols="12" md="8">
                    <v-card class="pa-3">
                      <div class="d-flex align-center justify-space-between">
                        <div class="text-subtitle-2">Objects</div>
                        <v-btn size="small" @click="addObject"
                          ><v-icon start>mdi-plus</v-icon>Add Object</v-btn
                        >
                      </div>

                      <div
                        v-if="env.objects.length === 0"
                        class="text-center py-8"
                      >
                        <v-icon size="64" color="grey-lighten-1" class="mb-4"
                          >mdi-package-variant-closed</v-icon
                        >
                        <div class="text-h6 text-grey mb-2">No Objects Yet</div>
                        <div class="text-body-2 text-grey mb-4">
                          Add your first object to get started
                        </div>
                        <v-btn color="primary" @click="addObject">
                          <v-icon start>mdi-plus</v-icon>
                          Add First Object
                        </v-btn>
                      </div>

                      <v-table v-else density="compact" class="mt-2">
                        <thead>
                          <tr>
                            <th>ID</th>
                            <th>Class</th>
                            <th>Kind</th>
                            <th>Affordances</th>
                            <th></th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(obj, i) in env.objects" :key="obj.id">
                            <td>
                              <v-text-field
                                v-model="obj.id"
                                placeholder="object_id"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="obj.class"
                                placeholder="base.Object"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="obj.kind"
                                placeholder="production_job"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="obj.affordances"
                                placeholder="assign,dispatch,process"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-btn
                                icon
                                size="x-small"
                                @click="removeObject(i)"
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

              <!-- STEP 5: SIMULATION SCRIPT -->
              <v-stepper-window-item :value="4">
                <v-row>
                  <v-col cols="12" md="8">
                    <v-card class="pa-3">
                      <v-card-title>Simulation Script</v-card-title>
                      <div class="d-flex justify-space-between mb-2">
                        <span class="text-subtitle-2">Script Steps</span>
                        <v-btn size="small" @click="addScriptStep">
                          <v-icon start>mdi-plus</v-icon>Add Step
                        </v-btn>
                      </div>

                      <div
                        v-if="env.script.length === 0"
                        class="text-center py-8"
                      >
                        <v-icon size="64" color="grey-lighten-1" class="mb-4"
                          >mdi-script-text</v-icon
                        >
                        <div class="text-h6 text-grey mb-2">
                          No Script Steps Yet
                        </div>
                        <div class="text-body-2 text-grey mb-4">
                          Define the sequence of actions for your simulation
                        </div>
                        <v-btn color="primary" @click="addScriptStep">
                          <v-icon start>mdi-plus</v-icon>
                          Add First Step
                        </v-btn>
                      </div>

                      <v-table v-else density="compact" class="mt-2">
                        <thead>
                          <tr>
                            <th>Time (t)</th>
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
                          <tr v-for="(step, i) in env.script" :key="i">
                            <td>
                              <v-text-field
                                v-model.number="step.t"
                                type="number"
                                step="0.1"
                                placeholder="0.0"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-select
                                :items="agentOptions"
                                v-model="step.agent"
                                placeholder="Select agent"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="step.action"
                                placeholder="view"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-select
                                :items="objectOptions"
                                v-model="step.object"
                                placeholder="Select object"
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model="step.effect_json"
                                placeholder='{"result":"value"}'
                                hide-details
                                density="compact"
                              />
                            </td>
                            <td>
                              <v-text-field
                                v-model.number="step.latency_ms"
                                type="number"
                                placeholder="1000"
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
                              <v-btn
                                icon
                                size="x-small"
                                @click="removeScriptStep(i)"
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

              <!-- STEP 5: RUN & EVALUATE -->
              <v-stepper-window-item :value="5">
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
                      <div class="d-flex gap-2 mb-2">
                        <v-btn
                          color="primary"
                          variant="outlined"
                          @click="onSaveConfig"
                        >
                          <v-icon start>mdi-content-save</v-icon> Save Config
                        </v-btn>
                        <v-btn
                          color="success"
                          :loading="busy"
                          @click="onRunSimulation"
                        >
                          <v-icon start>mdi-play</v-icon> Run Simulation
                        </v-btn>
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        <strong>Save Config:</strong> Saves to
                        <strong>/configs</strong> directory for later use.<br />
                        <strong>Run Simulation:</strong> Executes directly and
                        shows results below.
                      </div>
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

            <!-- Stepper Actions moved inside stepper window -->
            <div class="stepper-actions-container pa-4">
              <v-divider class="mb-4" />
              <div class="stepper-debug-info text-caption mb-2">
                DEBUG: Current Step: {{ step }} | Next Disabled:
                {{ step === 5 }}
              </div>
              <div class="d-flex justify-space-between">
                <v-btn variant="tonal" @click="prev" :disabled="step === 1">
                  <v-icon start>mdi-arrow-left</v-icon>
                  Back
                </v-btn>
                <v-btn
                  v-if="step < 5"
                  color="primary"
                  @click="next"
                  :disabled="step === 5"
                  class="next-button-debug"
                >
                  Next
                  <v-icon end>mdi-arrow-right</v-icon>
                </v-btn>
              </div>
            </div>
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
  getHAICPilotConfigs,
  loadHAICPilotConfig,
} from "@/services/envBuilderService";
import { computeCoreV1 } from "@/services/coreMetricsService";

export default {
  name: "EnvBuilderPage",
  components: { BaseLayout, CoreMetricsSummary },
  data() {
    return {
      activeTab: "env-builder",
      scriptedStep: 1,
      step: 1,
      env: {
        name: "My Environment",
        version: "v1",
        metrics: { rt_max: 5.0, baseline_s: null },
        agents: [
          {
            id: "human1",
            type: "human",
            profile: "default",
            affordances: "view,analyze,decide",
          },
          {
            id: "ai1",
            type: "ai",
            profile: "gpt",
            affordances: "classify,predict,analyze",
          },
        ],
        objects: [],
        tasks: [],
        script: [],
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
      // Environment loading
      envFile: null,
      envJson: "",
      selectedTemplate: null,
      selectedPilot: null,
      envTemplates: [
        { key: "medical", name: "Medical Diagnosis Environment" },
        { key: "manufacturing", name: "Manufacturing Environment" },
        { key: "finance", name: "Financial Analysis Environment" },
        { key: "education", name: "Educational Assessment Environment" },
      ],
      haicPilots: [],
    };
  },
  computed: {
    agentOptions() {
      return this.env.agents.map((a) => a.id);
    },
    objectOptions() {
      return this.env.objects.map((o) => o.id);
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
      console.log("Next button clicked, current step:", this.step);
      const newStep = Math.min(5, this.step + 1);
      console.log("Advancing to step:", newStep);
      this.step = newStep;
    },
    prev() {
      console.log("Prev button clicked, current step:", this.step);
      const newStep = Math.max(1, this.step - 1);
      console.log("Going back to step:", newStep);
      this.step = newStep;
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
        affordances: "view,analyze,decide",
      });
    },
    removeAgent(i) {
      this.env.agents.splice(i, 1);
    },

    addObject() {
      this.env.objects.push({
        id: `obj${this.env.objects.length + 1}`,
        class: "base.Object",
        kind: "resource",
        affordances: "use,access,modify",
      });
    },
    removeObject(i) {
      this.env.objects.splice(i, 1);
    },

    addScriptStep() {
      this.env.script.push({
        t: this.env.script.length + 1,
        agent: this.agentOptions[0] || "",
        action: "view",
        object: this.objectOptions[0] || "",
        effect_json: '{"result":"value"}',
        latency_ms: 1000,
        correct: true,
      });
    },
    removeScriptStep(i) {
      this.env.script.splice(i, 1);
    },

    // Environment loading methods
    async loadEnvFromFile() {
      if (!this.envFile || !this.envFile[0]) return;

      try {
        const file = this.envFile[0];
        const text = await file.text();
        let parsed;

        if (file.name.endsWith(".json")) {
          parsed = JSON.parse(text);
        } else {
          // For YAML files, we'll need to parse as JSON for now
          // In a full implementation, you'd use a YAML parser
          parsed = JSON.parse(text);
        }

        this.loadEnvironmentData(parsed);
        this.success = `Loaded environment from ${file.name}`;
      } catch (e) {
        this.error = `Failed to load file: ${e.message}`;
      }
    },

    loadTemplate(templateKey) {
      if (!templateKey) return;

      const templates = {
        medical: {
          name: "Medical Diagnosis Environment",
          version: "v1",
          metrics: { rt_max: 5.0, baseline_s: 2.0 },
          agents: [
            { id: "radiologist", type: "human", profile: "expert" },
            { id: "ai_assistant", type: "ai", profile: "gpt-4" },
          ],
          tasks: [
            {
              id: "diagnosis_task",
              name: "CT Scan Diagnosis",
              actions: [
                {
                  id: "view_scan",
                  name: "View CT Scan",
                  actor: "radiologist",
                  duration_s: 2.0,
                  correct: true,
                },
                {
                  id: "ai_analysis",
                  name: "AI Analysis",
                  actor: "ai_assistant",
                  latency_ms: 800,
                  correct: true,
                },
                {
                  id: "final_diagnosis",
                  name: "Final Diagnosis",
                  actor: "radiologist",
                  duration_s: 1.5,
                  correct: true,
                },
              ],
            },
          ],
        },
        manufacturing: {
          name: "Manufacturing Environment",
          version: "v1",
          metrics: { rt_max: 3.0, baseline_s: 1.5 },
          agents: [
            { id: "operator", type: "human", profile: "skilled" },
            { id: "quality_ai", type: "ai", profile: "vision-model" },
          ],
          tasks: [
            {
              id: "quality_check",
              name: "Quality Inspection",
              actions: [
                {
                  id: "manual_check",
                  name: "Manual Inspection",
                  actor: "operator",
                  duration_s: 1.2,
                  correct: true,
                },
                {
                  id: "ai_check",
                  name: "AI Inspection",
                  actor: "quality_ai",
                  latency_ms: 500,
                  correct: true,
                },
              ],
            },
          ],
        },
        finance: {
          name: "Financial Analysis Environment",
          version: "v1",
          metrics: { rt_max: 10.0, baseline_s: 5.0 },
          agents: [
            { id: "analyst", type: "human", profile: "senior" },
            { id: "risk_ai", type: "ai", profile: "financial-model" },
          ],
          tasks: [
            {
              id: "risk_assessment",
              name: "Risk Assessment",
              actions: [
                {
                  id: "data_review",
                  name: "Data Review",
                  actor: "analyst",
                  duration_s: 3.0,
                  correct: true,
                },
                {
                  id: "ai_modeling",
                  name: "AI Modeling",
                  actor: "risk_ai",
                  latency_ms: 2000,
                  correct: true,
                },
                {
                  id: "final_report",
                  name: "Final Report",
                  actor: "analyst",
                  duration_s: 2.5,
                  correct: true,
                },
              ],
            },
          ],
        },
        education: {
          name: "Educational Assessment Environment",
          version: "v1",
          metrics: { rt_max: 15.0, baseline_s: 8.0 },
          agents: [
            { id: "teacher", type: "human", profile: "experienced" },
            { id: "grading_ai", type: "ai", profile: "nlp-model" },
          ],
          tasks: [
            {
              id: "essay_grading",
              name: "Essay Grading",
              actions: [
                {
                  id: "read_essay",
                  name: "Read Essay",
                  actor: "teacher",
                  duration_s: 4.0,
                  correct: true,
                },
                {
                  id: "ai_analysis",
                  name: "AI Content Analysis",
                  actor: "grading_ai",
                  latency_ms: 3000,
                  correct: true,
                },
                {
                  id: "assign_grade",
                  name: "Assign Grade",
                  actor: "teacher",
                  duration_s: 1.0,
                  correct: true,
                },
              ],
            },
          ],
        },
      };

      const template = templates[templateKey];
      if (template) {
        this.loadEnvironmentData(template);
        this.success = `Loaded ${template.name} template`;
      }
    },

    parseEnvJson() {
      try {
        const parsed = JSON.parse(this.envJson);
        this.loadEnvironmentData(parsed);
        this.success = "JSON parsed and loaded successfully";
      } catch (e) {
        this.error = `JSON parsing failed: ${e.message}`;
      }
    },

    parseEnvYaml() {
      try {
        // For now, treat as JSON since we don't have YAML parser in frontend
        // In production, you'd use a YAML library like js-yaml
        const parsed = JSON.parse(this.envJson);
        this.loadEnvironmentData(parsed);
        this.success = "YAML parsed and loaded successfully";
      } catch (e) {
        this.error = `YAML parsing failed: ${e.message}`;
      }
    },

    loadEnvironmentData(data) {
      console.log("Loading environment data:", data);

      if (data.name) this.env.name = data.name;
      if (data.version) this.env.version = data.version;
      if (data.metrics)
        this.env.metrics = { ...this.env.metrics, ...data.metrics };

      // Handle agents with proper affordances format
      if (data.agents) {
        this.env.agents = data.agents.map((agent) => ({
          id: agent.id || agent.name,
          type: agent.type || (agent.model === "ai" ? "ai" : "human"),
          profile: agent.profile || agent.class || "default",
          affordances: Array.isArray(agent.affordances)
            ? agent.affordances.join(",")
            : agent.affordances || "view,analyze",
        }));
      }

      // Handle objects
      if (data.objects) {
        this.env.objects = Object.entries(data.objects || {}).map(
          ([id, obj]) => ({
            id: id,
            class: obj.class || "base.Object",
            kind: obj.attributes?.kind || obj.kind || "resource",
            affordances: Array.isArray(obj.affordances)
              ? obj.affordances.join(",")
              : obj.affordances || "use,access",
          })
        );
      } else {
        this.env.objects = [];
      }

      // Handle tasks
      if (data.tasks) {
        this.env.tasks = data.tasks.map((task) => ({
          id: task.id,
          name: task.name,
          actions: (task.actions || []).map((action) => ({
            id: action.id,
            name: action.name || action.action, // Use action name or fallback to action type
            actor: action.actor || action.agent, // Map actor/agent field
            duration_s: action.duration_s || 1.0,
            latency_ms: action.latency_ms,
            correct: action.correct !== undefined ? action.correct : true,
          })),
        }));
      }

      // Handle script (convert from HAIC format if needed)
      if (data.script) {
        this.env.script = data.script.map((step, index) => ({
          t: step.t || index + 1,
          agent: step.agent || step.actor,
          action: step.action,
          object: step.object,
          effect_json:
            typeof step.effect_json === "string"
              ? step.effect_json
              : step.effect
              ? JSON.stringify(step.effect)
              : '{"result":"value"}',
          latency_ms: step.latency_ms || 1000,
          correct: step.correct !== undefined ? step.correct : true,
        }));
      } else {
        this.env.script = [];
      }

      console.log("Environment loaded:", this.env);
    },

    async loadHAICPilot(pilotName) {
      if (!pilotName) return;

      try {
        const result = await loadHAICPilotConfig(pilotName);
        this.loadEnvironmentData(result.config);
        this.success = `Loaded HAIC pilot: ${pilotName}`;
      } catch (e) {
        this.error = `Failed to load HAIC pilot: ${e.message}`;
      }
    },

    getDomainColor(domain) {
      const colors = {
        medical: "teal",
        manufacturing: "orange",
        finance: "green",
        education: "purple",
        general: "blue",
      };
      return colors[domain] || "grey";
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

    // Save config methods
    async onSaveConfig() {
      this.error = "";
      this.success = "";
      this.busy = true;
      try {
        console.log("Starting config generation...");

        // Transform env object to match backend API expectations
        const configRequest = {
          task_name: this.env.name,
          task_description: `Environment version ${this.env.version}`,
          task_parameters: {
            domain: this.extractDomainFromTasks(),
            metrics: this.env.metrics,
          },
          agent_definitions: this.env.agents.map((agent) => ({
            name: agent.id, // Backend expects 'name' not 'id'
            type: agent.type,
            profile: agent.profile,
          })),
          profile_definitions: [], // Not used in current env builder
          filename: this.generateDescriptiveFilename(),
        };

        console.log("Config request:", configRequest);
        const gen = await generateEnvConfig(configRequest);
        console.log("Config saved:", gen);
        this.success = `Environment config saved successfully: ${gen.path}`;
      } catch (e) {
        console.error("Error in onSaveConfig:", e);
        this.error =
          e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          String(e);
      } finally {
        this.busy = false;
      }
    },

    // Run simulation directly
    async onRunSimulation() {
      this.error = "";
      this.success = "";
      this.artifact = null;
      this.busy = true;
      try {
        console.log("Starting direct simulation...");

        // First generate config
        const configRequest = {
          task_name: this.env.name,
          task_description: `Environment version ${this.env.version}`,
          task_parameters: {
            domain: this.extractDomainFromTasks(),
            metrics: this.env.metrics,
          },
          agent_definitions: this.env.agents.map((agent) => ({
            name: agent.id, // Backend expects 'name' not 'id'
            type: agent.type,
            profile: agent.profile,
          })),
          profile_definitions: [], // Not used in current env builder
          filename: `${this.env.name
            .toLowerCase()
            .replace(/\s+/g, "_")}_env.yaml`,
        };

        console.log("Generating config for simulation:", configRequest);
        const gen = await generateEnvConfig(configRequest);
        console.log("Config generated:", gen);

        // Then run simulation
        console.log("Starting simulation run...");
        const run = await runSimulation(gen.path);
        console.log("Simulation run result:", run);

        // Compute metrics
        console.log("Computing metrics...");
        const art = await computeCoreV1(run.run_id, {
          rt_max: this.env.metrics.rt_max,
          baseline_s: this.env.metrics.baseline_s,
        });
        console.log("Metrics computed:", art);

        this.artifact = art;
        this.success =
          "Environment built and simulation completed successfully! Config also saved.";
      } catch (e) {
        console.error("Error in onRunSimulation:", e);
        this.error =
          e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          String(e);
      } finally {
        this.busy = false;
      }
    },

    // Run methods
    async onGenerateAndRun() {
      this.error = "";
      this.success = "";
      this.artifact = null;
      this.busy = true;
      try {
        console.log("Starting config generation...");

        // Transform env object to match backend API expectations
        const configRequest = {
          task_name: this.env.name,
          task_description: `Environment version ${this.env.version}`,
          task_parameters: {
            domain: this.extractDomainFromTasks(),
            metrics: this.env.metrics,
          },
          agent_definitions: this.env.agents.map((agent) => ({
            id: agent.id,
            type: agent.type,
            profile: agent.profile,
          })),
          profile_definitions: [], // Not used in current env builder
          filename: `${this.env.name
            .toLowerCase()
            .replace(/\s+/g, "_")}_env.yaml`,
        };

        console.log("Config request:", configRequest);
        const gen = await generateEnvConfig(configRequest);
        console.log("Config generated:", gen);
        this.success = `Config generated: ${gen.path}`;

        console.log("Starting simulation run...");
        const run = await runSimulation(gen.path);
        console.log("Simulation run result:", run);

        console.log("Computing metrics...");
        const art = await computeCoreV1(run.run_id, {
          rt_max: this.env.metrics.rt_max,
          baseline_s: this.env.metrics.baseline_s,
        });
        console.log("Metrics computed:", art);

        this.artifact = art;
        this.success =
          "Environment built and simulation completed successfully!";
      } catch (e) {
        console.error("Error in onGenerateAndRun:", e);
        this.error =
          e?.response?.data?.detail ||
          e?.response?.data?.message ||
          e?.message ||
          String(e);
      } finally {
        this.busy = false;
      }
    },

    extractDomainFromTasks() {
      // Try to extract domain from task names or use default
      const taskNames = this.env.tasks.map((t) => t.name.toLowerCase());
      if (
        taskNames.some(
          (name) => name.includes("medical") || name.includes("diagnosis")
        )
      ) {
        return "medical";
      }
      if (
        taskNames.some(
          (name) => name.includes("manufactur") || name.includes("quality")
        )
      ) {
        return "manufacturing";
      }
      if (
        taskNames.some(
          (name) => name.includes("risk") || name.includes("financial")
        )
      ) {
        return "finance";
      }
      if (
        taskNames.some(
          (name) => name.includes("grade") || name.includes("education")
        )
      ) {
        return "education";
      }
      return "general";
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

    generateDescriptiveFilename() {
      // Generate descriptive filename from environment elements
      const domain = this.extractDomainFromTasks();
      const envName = this.env.name.toLowerCase().replace(/[^a-z0-9]/g, "_");
      const agentCount = this.env.agents.length;
      const version = this.env.version || "v1";

      // Format: {domain}_{env_name}_{agent_count}agents_{version}.yaml
      return `${domain}_${envName}_${agentCount}agents_${version}.yaml`;
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
  async mounted() {
    try {
      const response = await getHAICPilotConfigs();
      this.haicPilots = response.pilots;
    } catch (e) {
      console.error("Failed to load HAIC pilot configs:", e);
    }
  },
};
</script>

<style scoped>
pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", monospace;
}

/* Task expansion panel styles */
.v-expansion-panel {
  border-radius: 8px !important;
  overflow: visible !important;
}

.v-expansion-panel-text {
  padding: 0 !important;
}

/* Action table styles */
.actions-table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid rgb(var(--v-theme-surface-variant));
}

.actions-table {
  min-width: 600px;
  background: transparent;
}

.action-row:hover {
  background-color: rgb(var(--v-theme-surface-variant)) !important;
}

.action-input {
  min-width: 120px;
}

.action-name-cell {
  min-width: 150px;
}

.action-actor-cell {
  min-width: 130px;
}

.action-duration-cell,
.action-latency-cell {
  min-width: 110px;
}

.action-correct-cell {
  min-width: 120px;
}

.action-controls-cell {
  min-width: 120px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .action-input {
    min-width: 100px;
  }

  .actions-table {
    min-width: 500px;
  }
}
</style>
