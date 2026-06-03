<template>
  <BaseLayout>
    <v-container fluid>
      <v-row>
        <v-col>
          <h1 class="text-h4 mb-2">
            Visualization for Configuration ID: {{ configId }}
          </h1>
          <p class="subtitle-1 mb-1">
            Explore metrics by group or switch to Core HAIC metrics.
          </p>

          <!-- Mode toggle -->
          <div class="d-flex align-center ga-4 mb-4">
            <v-switch
              v-model="coreMode"
              inset
              color="primary"
              :label="
                coreMode
                  ? 'Core (minimal) metrics'
                  : 'Outcome (extended) metrics'
              "
            />
          </div>
        </v-col>
      </v-row>

      <!-- ── EMPTY STATE ─────────────────────────────────────────────── -->
      <v-row v-if="hasNoData && !isLoading">
        <v-col>
          <EmptyState
            icon="mdi-chart-areaspline"
            title="No evaluation runs yet"
            message="This configuration has no runs to visualize. The platform computes metrics like Trust, Cognitive Load, Adaptability, and more — once you have data."
            hint="Upload a log file and trigger an evaluation to see charts here."
            actionLabel="Upload a Log"
            actionTo="/logs/upload"
            actionIcon="mdi-upload"
          />
        </v-col>
      </v-row>

      <!-- ── CHARTS (only shown when there is data) ─────────────────── -->
      <template v-else>
        <v-row>
          <!-- Sidebar -->
          <v-col cols="2">
            <v-list density="compact">
              <v-list-item
                v-for="group in groupOptions"
                :key="group.value"
                @click="selectedGroup = group.value"
                :class="{ 'selected-group': selectedGroup === group.value }"
                :title="groupedMetrics?.[group.value]?.group_description || ''"
                style="cursor: pointer"
              >
                <template #prepend>
                  <v-icon>{{ getGroupIcon(group.value) }}</v-icon>
                </template>
                <v-list-item-title class="text-caption">
                  {{ group.title }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>

          <!-- Charts -->
          <v-col cols="10">
            <v-row>
              <v-col
                v-for="(metric, index) in selectedMetrics"
                :key="index"
                cols="10"
                md="6"
              >
                <!-- Metric header with optional info tooltip -->
                <div class="d-flex align-center ga-2 mb-2">
                  <h3 class="text-h6">{{ labelFor(metric) }}</h3>

                  <!-- ⓘ tooltip — shown in core mode for known metrics -->
                  <v-tooltip
                    v-if="coreMode && metricInfo[metric]"
                    location="top"
                    max-width="320"
                  >
                    <template #activator="{ props }">
                      <v-icon
                        v-bind="props"
                        size="18"
                        color="info"
                        style="cursor: help; flex-shrink: 0"
                      >
                        mdi-information-outline
                      </v-icon>
                    </template>

                    <div>
                      <div class="font-weight-bold mb-1">
                        {{ metricInfo[metric].fullName }}
                      </div>
                      <div class="mb-1">
                        {{ metricInfo[metric].description }}
                      </div>
                      <div class="text-caption" style="opacity: 0.8">
                        Range: {{ metricInfo[metric].range }}
                      </div>
                    </div>
                  </v-tooltip>
                </div>

                <p class="text-caption mb-2" style="min-height: 32px">
                  {{
                    metricDescriptions?.[selectedGroup]?.[metric] ??
                    "No description"
                  }}
                </p>

                <ChartComponent
                  v-if="chartData[metric]"
                  :chartId="'chart-' + index"
                  :chartData="chartData[metric]"
                  :chartType="'line'"
                  :chartOptions="getChartOptions(metric)"
                />
                <div v-else class="text-caption text-medium-emphasis">
                  No data yet for this metric.
                </div>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </template>

      <v-row>
        <v-col cols="12" class="text-center">
          <v-btn color="primary" @click="goBack">Back</v-btn>
        </v-col>
      </v-row>

      <v-overlay :value="isLoading">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
      </v-overlay>

      <v-snackbar v-model="snackbar" :color="snackbarColor" top>
        {{ snackbarText }}
        <template #action="{ attrs }">
          <v-btn text v-bind="attrs" @click="snackbar = false">Close</v-btn>
        </template>
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script>
import ChartComponent from "@/components/PlotChart.vue";
import EmptyState from "@/components/EmptyState.vue";
import resultService from "@/services/resultService";
import evaluationService from "@/services/evaluationService";
import BaseLayout from "@/components/BaseLayout.vue";

const CORE_GROUP = "Core HAIC";

export default {
  components: { ChartComponent, EmptyState, BaseLayout },
  data() {
    return {
      configId: null,
      coreMode: false,
      selectedGroup: null,
      groupOptions: [],
      groupedMetrics: {},
      metricDescriptions: {},
      chartData: {},
      labels: [],
      selectedMetrics: [],
      runData: [],

      // ── Metric info for tooltips (Problem 2) ────────────────────────
      metricInfo: {
        F: {
          fullName: "Interaction Frequency",
          description:
            "How many human-AI interactions happen per minute. Higher = more active collaboration.",
          range: "Higher is better",
        },
        D: {
          fullName: "Avg. Action Duration",
          description:
            "Average time per action in seconds. Higher = slower interactions, possible bottlenecks.",
          range: "Lower is better",
        },
        HCL: {
          fullName: "Human Cognitive Load proxy",
          description:
            "Proxy for how much mental effort the human is spending. Higher means the human is carrying less burden.",
          range: "0–1, higher = less load",
        },
        Tr: {
          fullName: "Trust proxy",
          description:
            "How often humans accept AI suggestions without overriding. Reflects confidence in the AI system.",
          range: "0–1, higher = more trust",
        },
        A: {
          fullName: "Adaptability Δ",
          description:
            "Whether collaboration quality improved over the session. Positive values indicate the team is learning and improving.",
          range: "-1 to 1, positive = improving",
        },
        S: {
          fullName: "Similarity",
          description:
            "How closely surrogate agents replicate human behavior (simulation only).",
          range: "0–1",
        },
        EL: {
          fullName: "Effort Loss",
          description:
            "How much slower the collaboration is compared to the baseline. Zero means no loss.",
          range: "0 = no loss, higher = worse",
        },
        EfficiencyScore: {
          fullName: "Efficiency Score",
          description:
            "Normalized efficiency combining Effort Loss and other signals into a single score.",
          range: "0–1, higher = better",
        },
      },

      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: "nearest" },
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label(ctx) {
                const v = ctx.parsed?.y;
                return `${ctx.dataset.label}: ${v == null ? "N/A" : v}`;
              },
            },
          },
        },
        scales: { y: { beginAtZero: true } },
      },
      isLoading: false,
      snackbar: false,
      snackbarText: "",
      snackbarColor: "info",
    };
  },

  computed: {
    // True when loading is done and there are no runs to show (Problem 1)
    hasNoData() {
      return !this.isLoading && this.runData.length === 0;
    },
  },

  mounted() {
    this.configId = this.$route.params.configId;
    this.bootstrap();
  },

  methods: {
    labelFor(metric) {
      const map = {
        EL: "EL (Efficiency Loss, ↑ worse)",
        D: "D (Avg. Action Duration, s)",
        F: "F (Interactions/min)",
        HCL: "HCL (Human Cognitive Load proxy)",
        Tr: "Tr (Trust proxy)",
        A: "A (Adaptability Δ)",
        S: "S (Similarity)",
        EfficiencyScore: "EfficiencyScore (normalized)",
      };
      return map[metric] || metric;
    },

    async bootstrap() {
      this.isLoading = true;
      try {
        await this.fetchRuns();
        if (!this.coreMode) {
          await this.fetchMetricGroups();
        } else {
          this.prepareCoreGroups();
        }
        await this.populateAllRuns();
      } catch (e) {
        console.error(e);
        this.showMessage("Failed to load data.", "error");
      } finally {
        this.isLoading = false;
      }
    },

    _finiteVals(metric) {
      const arr = this.chartData?.[metric]?.datasets?.[0]?.data || [];
      return arr.filter((v) => Number.isFinite(v));
    },
    _niceHeadroomMax(values, fallback = 1) {
      const max = Math.max(...values, 0);
      const base = max || fallback;
      const head = base * 1.2;
      const mag = Math.pow(10, Math.floor(Math.log10(head || 1)));
      const steps = [1, 2, 5, 10].map((s) => s * mag);
      const nice = steps.find((s) => head <= s) ?? steps[steps.length - 1];
      return nice;
    },

    getChartOptions(metricName) {
      const base = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: (ctx) =>
                ctx.raw === null || ctx.raw === undefined
                  ? "N/A"
                  : `${ctx.raw}`,
            },
          },
        },
      };

      if (this.coreMode) {
        const zeroToOne = new Set(["HCL", "Tr", "S", "EfficiencyScore"]);
        const seconds = new Set(["D"]);
        const unbounded = new Set(["F", "EL"]);

        if (zeroToOne.has(metricName)) {
          return {
            ...base,
            scales: {
              y: {
                beginAtZero: true,
                max: 1,
                ticks: { callback: (v) => Number(v).toFixed(2) },
              },
            },
          };
        }

        if (metricName === "A") {
          return {
            ...base,
            scales: {
              y: {
                min: -1,
                max: 1,
                ticks: { callback: (v) => Number(v).toFixed(2) },
              },
            },
          };
        }

        if (seconds.has(metricName)) {
          const vals = this._finiteVals(metricName);
          const suggested = this._niceHeadroomMax(vals, 1);
          return {
            ...base,
            scales: {
              y: {
                beginAtZero: true,
                suggestedMax: suggested,
                ticks: { callback: (v) => `${v} s` },
              },
            },
          };
        }

        if (unbounded.has(metricName)) {
          const vals = this._finiteVals(metricName);
          const suggested = this._niceHeadroomMax(
            vals,
            metricName === "F" ? 10 : 1
          );
          return {
            ...base,
            scales: {
              y: {
                beginAtZero: true,
                suggestedMax: suggested,
              },
            },
          };
        }

        return {
          ...base,
          scales: { y: { beginAtZero: true } },
        };
      }

      const timeMetrics = new Set([
        "Response Time",
        "Task Completion Time",
        "Time to Resolution",
      ]);
      const countMetrics = new Set(["Safety Incidents"]);

      if (timeMetrics.has(metricName)) {
        return {
          ...base,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { callback: (v) => `${v} s` },
            },
          },
        };
      }

      if (countMetrics.has(metricName)) {
        return {
          ...base,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { precision: 0, stepSize: 1 },
            },
          },
        };
      }

      return {
        ...base,
        scales: {
          y: {
            beginAtZero: true,
            max: 1,
            ticks: { callback: (v) => Number(v).toFixed(2) },
          },
        },
      };
    },

    async fetchRuns() {
      const { data } = await resultService.getResultsByConfig(this.configId);
      this.runData = data || [];
      const labels = (this.runData || [])
        .map((r) => r.ai_model_version)
        .filter(Boolean);
      this.labels = [...new Set(labels)].sort((a, b) =>
        a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" })
      );
    },

    async fetchMetricGroups() {
      this.isLoading = true;
      const { data } = await evaluationService.getMetrics();
      this.groupedMetrics = data || {};
      const descMap = {};
      Object.entries(this.groupedMetrics).forEach(([group, payload]) => {
        const inner = {};
        (payload.metrics || []).forEach((m) => {
          inner[m.name] = m.description ?? null;
        });
        descMap[group] = inner;
      });
      this.metricDescriptions = descMap;

      this.groupOptions = Object.keys(this.groupedMetrics).map((group) => ({
        title: group,
        value: group,
      }));
      this.selectedGroup = this.groupOptions[0]?.value || null;
      this.updateSelectedMetrics();
      this.isLoading = false;
    },

    prepareCoreGroups() {
      this.groupOptions = [{ title: CORE_GROUP, value: CORE_GROUP }];
      this.selectedGroup = CORE_GROUP;
      this.selectedMetrics = [
        "F",
        "D",
        "HCL",
        "Tr",
        "A",
        "S",
        "EL",
        "EfficiencyScore",
      ];
    },

    updateSelectedMetrics() {
      if (this.coreMode) return;
      if (this.selectedGroup && this.groupedMetrics[this.selectedGroup]) {
        this.selectedMetrics = this.groupedMetrics[
          this.selectedGroup
        ].metrics.map((m) => m.name);
      } else {
        this.selectedMetrics = [];
      }
    },

    async populateAllRuns() {
      this.chartData = {};
      this.selectedMetrics.forEach((metric, idx) => {
        this.chartData[metric] = {
          labels: this.labels,
          datasets: [
            {
              label: this.labelFor(metric),
              data: new Array(this.labels.length).fill(null),
              fill: false,
              borderColor: this.getChartColor(idx),
              tension: 0.1,
            },
          ],
        };
      });
      for (const run of this.runData) {
        if (!run?.id) continue;
        await this.populateRun(run);
      }
      this.chartData = { ...this.chartData };
    },

    async populateRun(run) {
      const { data } = await resultService.getResultDetail(
        this.configId,
        run.id
      );
      if (!data) return;
      const source = this.coreMode
        ? data.aggregates?.interaction || {}
        : data.aggregates?.by_group || {};
      const version = run.ai_model_version;
      const idx = this.labels.indexOf(version);
      if (idx === -1) return;

      if (this.coreMode) {
        this.selectedMetrics.forEach((metric) => {
          const val = source?.[metric] ?? null;
          if (metric in this.chartData)
            this.chartData[metric].datasets[0].data[idx] = val;
        });
      } else {
        const groupBlock = source?.[this.selectedGroup] || {};
        this.selectedMetrics.forEach((metric) => {
          const v = groupBlock?.[metric];
          if (metric in this.chartData) {
            this.chartData[metric].datasets[0].data[idx] = v ?? null;
          }
        });
      }
    },

    showMessage(text, color = "info") {
      this.snackbarText = text;
      this.snackbarColor = color;
      this.snackbar = true;
    },
    getGroupIcon(groupName) {
      const icons = {
        [CORE_GROUP]: "mdi-tune",
        Effectiveness: "mdi-chart-line",
        Efficiency: "mdi-speedometer",
        "Adaptability and Learning": "mdi-brain",
        "Collaboration and Interaction": "mdi-human-handsup",
        "Trust and Safety": "mdi-shield",
        "Robustness and Generalization": "mdi-robot",
      };
      return icons[groupName] || "mdi-information";
    },
    getChartColor(i) {
      const colors = [
        "#4CAF50",
        "#2196F3",
        "#FFC107",
        "#E91E63",
        "#9C27B0",
        "#00BCD4",
        "#FF5722",
        "#795548",
      ];
      return colors[i % colors.length];
    },
    goBack() {
      this.$router.go(-1);
    },
  },
  watch: {
    coreMode() {
      this.bootstrap();
    },
    selectedGroup() {
      if (this.coreMode) return;
      this.updateSelectedMetrics();
      this.populateAllRuns();
    },
  },
};
</script>

<style scoped>
.selected-group {
  background-color: #e0e0e0;
}
</style>
