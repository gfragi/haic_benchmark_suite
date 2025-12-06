<template>
  <BaseLayout>
    <v-container>
      <v-card class="mb-4">
        <v-card-title class="text-h6">HAIC Simulation Runner</v-card-title>
        <v-card-subtitle
          >Run Human-AI Collaboration simulations with JSON
          configurations</v-card-subtitle
        >
      </v-card>

      <!-- Instructions Card (always visible) -->
      <v-row v-if="!result">
        <v-col cols="12">
          <v-card class="mb-4">
            <v-card-title>Instructions</v-card-title>
            <v-card-text>
              <div class="text-body-2">
                <p>
                  Paste a valid HAIC simulation JSON configuration to run a
                  simulation.
                </p>
                <p>The configuration should include:</p>
                <ul>
                  <li><code>sim_id</code>: Simulation identifier</li>
                  <li><code>environment</code>: Environment settings</li>
                  <li><code>agents</code>: Array of agents (human/AI)</li>
                  <li><code>objects</code>: Array of simulation objects</li>
                  <li><code>script</code>: Array of simulation steps</li>
                </ul>
                <p>
                  Use the
                  <router-link to="/env-builder"
                    >Environment Builder</router-link
                  >
                  to create configurations visually.
                </p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Configuration and Results Layout -->
      <v-row v-if="!result">
        <!-- Configuration Section (No Results) -->
        <v-col cols="12" lg="8">
          <v-card class="pa-3">
            <v-card-title>Simulation Configuration</v-card-title>

            <!-- Predefined Config Selector -->
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="selectedConfig"
                  :items="configOptions"
                  label="Load Predefined Config (optional)"
                  item-title="name"
                  item-value="name"
                  clearable
                  density="comfortable"
                  @update:model-value="loadSelectedConfig"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="seed"
                  type="number"
                  label="Random Seed (optional)"
                  density="comfortable"
                  hint="Leave empty for random seed"
                />
              </v-col>
            </v-row>

            <v-textarea
              v-model="jsonConfig"
              label="JSON Configuration"
              placeholder='{"sim_id": "example", "environment": {...}, "agents": [...], "objects": [...], "script": [...]}'
              rows="15"
              density="comfortable"
              :error-messages="jsonError"
              @input="validateJson"
            />

            <v-divider class="my-3" />
            <v-btn
              color="primary"
              :loading="busy"
              @click="runSimulation"
              :disabled="!isValidJson"
            >
              <v-icon start>mdi-play</v-icon> Run Simulation
            </v-btn>
          </v-card>
        </v-col>

        <!-- Saved Results Sidebar -->
        <v-col cols="12" lg="4" v-if="savedResults.length > 0">
          <v-card class="pa-3">
            <v-card-title class="d-flex align-center justify-space-between">
              <span>Saved Results</span>
              <v-btn icon size="small" @click="clearAllResults" color="error">
                <v-icon>mdi-delete-sweep</v-icon>
              </v-btn>
            </v-card-title>

            <v-card-text class="pa-0">
              <v-list density="compact">
                <v-list-item
                  v-for="(savedResult, index) in savedResults"
                  :key="index"
                  @click="loadSavedResult(index)"
                  class="cursor-pointer"
                >
                  <template v-slot:prepend>
                    <v-icon color="success">mdi-chart-line</v-icon>
                  </template>

                  <v-list-item-title class="text-body-2">
                    {{ savedResult.simulation_result.sim_id }}
                  </v-list-item-title>

                  <v-list-item-subtitle class="text-caption">
                    {{ savedResult.configName }} •
                    {{ formatSavedDate(savedResult.savedAt) }}
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <v-btn
                      icon
                      size="small"
                      @click.stop="deleteSavedResult(index)"
                      color="error"
                    >
                      <v-icon size="small">mdi-delete</v-icon>
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Results Layout (Full Width) -->
      <v-row v-else>
        <v-col cols="12">
          <!-- Action Buttons -->
          <div class="d-flex gap-2 mb-4">
            <v-btn variant="outlined" @click="result = null">
              <v-icon start>mdi-arrow-left</v-icon>
              Back to Configuration
            </v-btn>
            <v-btn color="success" variant="outlined" @click="saveResult">
              <v-icon start>mdi-content-save</v-icon>
              Save Results
            </v-btn>
          </div>

          <!-- Results Display -->
          <HAICSimulationResults :result="result" />
        </v-col>
      </v-row>

      <v-alert v-if="error" type="error" class="mt-3">{{ error }}</v-alert>
      <v-alert v-if="success" type="success" class="mt-3">{{
        success
      }}</v-alert>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import HAICSimulationResults from "@/components/HAICSimulationResults.vue";
import {
  runHAICSimMVPConfig,
  getHAICConfigs,
  loadHAICConfig,
} from "@/services/envBuilderService";

export default {
  name: "SimulatorPage",
  components: { BaseLayout, HAICSimulationResults },
  data() {
    return {
      jsonConfig: `{
  "sim_id": "ct_demo",
  "environment": {
    "id": "CT_Diagnosis",
    "class": "base.Environment",
    "attributes": {
      "task": "classification",
      "domain": "medical"
    }
  },
  "agents": [
    {
      "id": "A1",
      "class": "user_plugins.medical.Radiologist",
      "model": "human",
      "attributes": {
        "viewed_cases": []
      },
      "affordances": ["view", "classify"]
    },
    {
      "id": "A2",
      "class": "base.Agent",
      "model": "ai",
      "attributes": {},
      "affordances": ["classify"]
    }
  ],
  "objects": [
    {
      "id": "O1",
      "class": "user_plugins.medical.CTImage",
      "attributes": {
        "type": "CT"
      },
      "affordances": ["view", "classify"]
    }
  ],
  "script": [
    {
      "t": 1,
      "agent": "A1",
      "action": "view",
      "object": "O1",
      "effect_json": "{}",
      "latency_ms": 2000,
      "correct": true
    },
    {
      "t": 2,
      "agent": "A2",
      "action": "classify",
      "object": "O1",
      "effect_json": "{\\"ai_label\\": \\"benign\\"}",
      "latency_ms": 500,
      "correct": true
    }
  ]
}`,
      seed: null,
      selectedConfig: null,
      configOptions: [],
      jsonError: "",
      isValidJson: true,
      busy: false,
      error: "",
      success: "",
      result: null,
      savedResults: [],
    };
  },
  computed: {
    prettyResult() {
      return this.result ? JSON.stringify(this.result, null, 2) : "";
    },
  },
  methods: {
    validateJson() {
      try {
        JSON.parse(this.jsonConfig);
        this.jsonError = "";
        this.isValidJson = true;
      } catch (e) {
        this.jsonError = "Invalid JSON: " + e.message;
        this.isValidJson = false;
      }
    },
    async loadConfigs() {
      try {
        const response = await getHAICConfigs();
        const options = [];
        // Add configs
        response.configs.forEach((config) => {
          options.push({
            name: config.name.replace(".json", ""),
            type: "config",
            title: `${config.name} (Config)`,
          });
        });
        // Add examples
        response.examples.forEach((example) => {
          options.push({
            name: example.name.replace(".json", ""),
            type: "example",
            title: `${example.name} (Example)`,
          });
        });
        this.configOptions = options;
      } catch (e) {
        console.error("Failed to load HAIC configs:", e);
        this.error =
          "Failed to load predefined configs: " + (e?.message || String(e));
      }
    },
    async loadSelectedConfig(configName) {
      if (!configName) return;

      try {
        const response = await loadHAICConfig(configName);
        this.jsonConfig = JSON.stringify(response.config, null, 2);
        this.validateJson();
      } catch (e) {
        this.error = `Failed to load config: ${
          e?.response?.data?.detail || e?.message || String(e)
        }`;
      }
    },
    async runSimulation() {
      this.error = "";
      this.success = "";
      this.result = null;
      this.busy = true;

      try {
        const config = JSON.parse(this.jsonConfig);
        const result = await runHAICSimMVPConfig(config, this.seed);
        this.success = "Simulation completed successfully!";
        this.result = result;
      } catch (e) {
        if (e instanceof SyntaxError) {
          this.error = "Invalid JSON configuration: " + e.message;
        } else {
          this.error = e?.response?.data?.detail || e?.message || String(e);
        }
      } finally {
        this.busy = false;
      }
    },
    saveResult() {
      if (!this.result) return;

      const savedResult = {
        ...this.result,
        savedAt: new Date().toISOString(),
        configName: this.selectedConfig || "Custom Config",
      };

      // Load existing saved results
      const existingResults = JSON.parse(
        localStorage.getItem("haic_simulation_results") || "[]"
      );

      // Add new result to the beginning
      existingResults.unshift(savedResult);

      // Keep only last 10 results
      const trimmedResults = existingResults.slice(0, 10);

      // Save back to localStorage
      localStorage.setItem(
        "haic_simulation_results",
        JSON.stringify(trimmedResults)
      );

      this.success = "Simulation results saved successfully!";
      this.loadSavedResults();
    },
    loadSavedResults() {
      try {
        this.savedResults = JSON.parse(
          localStorage.getItem("haic_simulation_results") || "[]"
        );
      } catch (e) {
        console.error("Failed to load saved results:", e);
        this.savedResults = [];
      }
    },
    loadSavedResult(index) {
      if (this.savedResults[index]) {
        this.result = this.savedResults[index];
        this.success = `Loaded saved result: ${this.result.simulation_result.sim_id}`;
      }
    },
    deleteSavedResult(index) {
      this.savedResults.splice(index, 1);
      localStorage.setItem(
        "haic_simulation_results",
        JSON.stringify(this.savedResults)
      );
      this.success = "Saved result deleted";
    },
    clearAllResults() {
      localStorage.removeItem("haic_simulation_results");
      this.savedResults = [];
      this.success = "All saved results cleared";
    },
    formatSavedDate(dateString) {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffHours = diffMs / (1000 * 60 * 60);

      if (diffHours < 1) {
        const diffMins = Math.floor(diffMs / (1000 * 60));
        return `${diffMins}m ago`;
      } else if (diffHours < 24) {
        return `${Math.floor(diffHours)}h ago`;
      } else {
        return date.toLocaleDateString();
      }
    },
  },
  async mounted() {
    this.validateJson();
    await this.loadConfigs();
    this.loadSavedResults();
  },
};
</script>

<style scoped>
pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", monospace;
  font-size: 0.875rem;
}
</style>
