<template>
  <div>
    <!-- Simulation Summary -->
    <v-card class="mb-4" variant="outlined">
      <v-card-title class="text-h6 d-flex align-center">
        <v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
        Simulation Results: {{ result.simulation_result.sim_id }}
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-card variant="outlined" class="pa-3 text-center">
              <div class="text-h4 text-primary mb-1">
                {{ result.simulation_result.decisions.length }}
              </div>
              <div class="text-caption text-medium-emphasis">
                Total Decisions
              </div>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card variant="outlined" class="pa-3 text-center">
              <div class="text-h4 text-success mb-1">
                {{ Object.keys(result.simulation_result.agents).length }}
              </div>
              <div class="text-caption text-medium-emphasis">Agents</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card variant="outlined" class="pa-3 text-center">
              <div class="text-h4 text-warning mb-1">
                {{ Object.keys(result.simulation_result.objects).length }}
              </div>
              <div class="text-caption text-medium-emphasis">Objects</div>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card variant="outlined" class="pa-3 text-center">
              <div class="text-h6 text-medium-emphasis mb-1">
                {{ formatTimestamp(result.simulation_result.timestamp) }}
              </div>
              <div class="text-caption text-medium-emphasis">Completed At</div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Environment Info -->
    <v-card class="mb-4" variant="outlined">
      <v-card-title>
        <v-icon class="mr-2">mdi-earth</v-icon>
        Environment
      </v-card-title>
      <v-card-text>
        <v-chip class="mr-2" color="primary" variant="elevated">{{
          result.simulation_result.env_id
        }}</v-chip>
        <v-chip class="mr-2" color="secondary" variant="elevated">{{
          result.simulation_result.attributes.task
        }}</v-chip>
        <v-chip variant="outlined">{{
          result.simulation_result.attributes.domain
        }}</v-chip>
      </v-card-text>
    </v-card>

    <!-- Agents -->
    <v-card class="mb-4" variant="outlined">
      <v-card-title>
        <v-icon class="mr-2">mdi-account-group</v-icon>
        Agents ({{ Object.keys(result.simulation_result.agents).length }})
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col
            v-for="(agent, agentId) in result.simulation_result.agents"
            :key="agentId"
            cols="12"
            md="6"
          >
            <v-card variant="outlined" class="pa-3">
              <div class="d-flex align-center mb-2">
                <v-icon :color="getAgentIconColor(agent.model)" class="mr-2">
                  {{ getAgentIcon(agent.model) }}
                </v-icon>
                <span class="text-h6">{{ agentId }}</span>
                <v-chip
                  size="small"
                  :color="getAgentModelColor(agent.model)"
                  class="ml-2"
                  variant="elevated"
                >
                  {{ agent.model }}
                </v-chip>
              </div>
              <div class="text-body-2 mb-2">
                <strong>Affordances:</strong> {{ agent.affordances.join(", ") }}
              </div>
              <div
                v-if="Object.keys(agent.attributes).length > 0"
                class="text-body-2"
              >
                <strong>Attributes:</strong>
                <pre class="text-caption bg-grey-lighten-4 pa-1 mt-1 rounded">{{
                  JSON.stringify(agent.attributes, null, 2)
                }}</pre>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Objects -->
    <v-card class="mb-4" variant="outlined">
      <v-card-title>
        <v-icon class="mr-2">mdi-package-variant</v-icon>
        Objects ({{ Object.keys(result.simulation_result.objects).length }})
      </v-card-title>
      <v-card-text>
        <v-simple-table>
          <thead>
            <tr>
              <th class="text-left">ID</th>
              <th class="text-left">Class</th>
              <th class="text-left">Kind</th>
              <th class="text-left">Affordances</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(obj, objId) in result.simulation_result.objects"
              :key="objId"
            >
              <td>{{ objId }}</td>
              <td>{{ obj.class || "N/A" }}</td>
              <td>{{ obj.attributes?.kind || "N/A" }}</td>
              <td>{{ obj.affordances?.join(", ") || "N/A" }}</td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-card-text>
    </v-card>

    <!-- HAIC Metrics -->
    <v-card
      class="mb-4"
      variant="outlined"
      v-if="result.haic_metrics && Object.keys(result.haic_metrics).length > 0"
    >
      <v-card-title>
        <v-icon class="mr-2" color="success">mdi-chart-bar</v-icon>
        HAIC Performance Metrics
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col
            v-for="(value, key) in result.haic_metrics"
            :key="key"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card variant="outlined" class="pa-3 text-center">
              <div class="text-h5 mb-1" :class="getMetricColorClass(key)">
                {{ formatMetricValue(value) }}
              </div>
              <div class="text-caption text-medium-emphasis font-weight-medium">
                {{ getMetricLabel(key) }}
              </div>
              <div class="text-caption text-medium-emphasis mt-1">
                {{ getMetricDescription(key) }}
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Metrics Interpretation -->
        <v-alert
          type="info"
          variant="tonal"
          class="mt-4"
          v-if="result.haic_metrics.HCL !== undefined"
        >
          <div class="text-body-2">
            <strong>HCL (Human-AI Collaboration Level):</strong>
            {{ formatMetricValue(result.haic_metrics.HCL) }} -
            {{ getHCLInterpretation(result.haic_metrics.HCL) }}
          </div>
        </v-alert>
      </v-card-text>
    </v-card>

    <!-- Decisions Timeline -->
    <v-card class="mb-4" variant="outlined">
      <v-card-title>
        <v-icon class="mr-2">mdi-timeline-clock</v-icon>
        Decision Timeline ({{ result.simulation_result.decisions.length }}
        decisions)
      </v-card-title>
      <v-card-text>
        <v-timeline density="compact">
          <v-timeline-item
            v-for="(decision, index) in result.simulation_result.decisions"
            :key="index"
            :dot-color="getDecisionColor(decision.correct)"
            size="small"
          >
            <div class="d-flex align-center mb-1">
              <span class="text-body-1 font-weight-bold mr-2"
                >t={{ decision.t }}</span
              >
              <v-chip size="small" color="primary" variant="outlined">{{
                decision.agent_id
              }}</v-chip>
              <span class="mx-2">→</span>
              <v-chip size="small" color="secondary" variant="outlined">{{
                decision.action
              }}</v-chip>
              <span class="mx-2">on</span>
              <v-chip size="small" color="accent" variant="outlined">{{
                decision.object_id
              }}</v-chip>
            </div>
            <div class="text-body-2 mb-1">
              <strong>Effect:</strong>
              <span class="text-caption">{{
                formatEffect(decision.effect)
              }}</span>
            </div>
            <div class="text-caption">
              Latency: {{ decision.latency_ms }}ms
              <span v-if="decision.correct !== null" class="ml-2">
                • Correct: {{ decision.correct ? "Yes" : "No" }}
              </span>
            </div>
          </v-timeline-item>
        </v-timeline>
      </v-card-text>
    </v-card>

    <!-- Raw JSON (Collapsible) -->
    <v-card>
      <v-card-title>
        <v-icon class="mr-2">mdi-code-json</v-icon>
        Raw JSON Results
        <v-spacer></v-spacer>
        <v-btn icon @click="showRawJson = !showRawJson">
          <v-icon>{{
            showRawJson ? "mdi-chevron-up" : "mdi-chevron-down"
          }}</v-icon>
        </v-btn>
      </v-card-title>
      <v-expand-transition>
        <div v-show="showRawJson">
          <v-card-text>
            <pre
              class="text-body-2 bg-grey-lighten-4 pa-2"
              style="max-height: 400px; overflow: auto; font-size: 0.75rem"
              >{{ prettyResult }}
            </pre>
          </v-card-text>
        </div>
      </v-expand-transition>
    </v-card>
  </div>
</template>

<script>
export default {
  name: "HAICSimulationResults",
  props: {
    result: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showRawJson: false,
    };
  },
  computed: {
    prettyResult() {
      return JSON.stringify(this.result, null, 2);
    },
  },
  methods: {
    formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleString();
    },
    getAgentIcon(model) {
      return model === "human" ? "mdi-account" : "mdi-robot";
    },
    getAgentIconColor(model) {
      return model === "human" ? "blue" : "green";
    },
    getAgentModelColor(model) {
      return model === "human" ? "blue" : "green";
    },
    getDecisionColor(correct) {
      if (correct === null) return "grey";
      return correct ? "green" : "red";
    },
    formatEffect(effect) {
      if (typeof effect === "object") {
        return Object.entries(effect)
          .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
          .join(", ");
      }
      return String(effect);
    },
    getMetricLabel(key) {
      const labels = {
        F: "Interaction Frequency",
        D: "Action Duration",
        HCL: "Human-AI Collaboration",
        Tr: "Trust",
        A: "Adaptability",
        S: "Surrogate Similarity",
        EL: "Efficiency Loss",
        EfficiencyScore: "Efficiency Score",
      };
      return labels[key] || key;
    },
    getMetricColorClass(key) {
      const colors = {
        F: "text-blue",
        D: "text-purple",
        HCL: "text-green",
        Tr: "text-orange",
        A: "text-success",
        S: "text-red",
        EL: "text-cyan",
        EfficiencyScore: "text-teal",
      };
      return colors[key] || "text-primary";
    },
    formatMetricValue(value) {
      if (typeof value === "number") {
        return value.toFixed(3);
      }
      return String(value);
    },
    getMetricDescription(key) {
      const descriptions = {
        F: "Agent interactions per minute (higher = more active)",
        D: "Average action duration in seconds (lower = faster)",
        HCL: "Human-AI collaboration level 0-1 (higher = better)",
        Tr: "Trust based on error rate 0-1 (higher = more reliable)",
        A: "Adaptability/learning improvement (positive = improving)",
        S: "AI similarity to human behavior 0-1 (higher = more human-like)",
        EL: "Efficiency loss vs baseline ≥0 (lower = more efficient)",
        EfficiencyScore: "Overall efficiency score 0-1 (higher = better)",
      };
      return descriptions[key] || "";
    },
    getHCLInterpretation(hcl) {
      if (hcl >= 0.9)
        return "Excellent collaboration - highly effective human-AI interaction";
      if (hcl >= 0.7)
        return "Good collaboration - effective human-AI partnership";
      if (hcl >= 0.5) return "Moderate collaboration - room for improvement";
      if (hcl >= 0.3) return "Low collaboration - significant issues detected";
      return "Poor collaboration - major improvements needed";
    },
  },
};
</script>

<style scoped>
.v-timeline-item {
  min-height: auto;
}

pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", monospace;
  font-size: 0.75rem;
}
</style>
