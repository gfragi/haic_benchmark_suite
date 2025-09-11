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

      <v-row>
        <!-- Sidebar -->
        <v-col cols="2">
          <v-list dense>
            <v-list-item
              v-for="group in groupOptions"
              :key="group.value"
              @click="selectedGroup = group.value"
              :class="{ 'selected-group': selectedGroup === group.value }"
              style="cursor: pointer"
            >
              <v-list-item>
                <v-icon>{{ getGroupIcon(group.value) }}</v-icon>
              </v-list-item>
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
              <h3 class="text-h6 mb-2">{{ metric }}</h3>
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
                :chartOptions="chartOptions"
              />
              <div v-else class="text-caption text-medium-emphasis">
                No data yet for this metric.
              </div>
            </v-col>
          </v-row>
        </v-col>
      </v-row>

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
import resultService from "@/services/resultService";
import evaluationService from "@/services/evaluationService";
import BaseLayout from "@/components/BaseLayout.vue";

const CORE_GROUP = "Core HAIC";

export default {
  components: { ChartComponent, BaseLayout },
  data() {
    return {
      configId: null,

      // mode
      coreMode: false,

      // grouping + selection
      selectedGroup: null,
      groupOptions: [],
      groupedMetrics: {}, // from /evaluate/metrics (for outcome mode)
      metricDescriptions: {}, // { [group]: { [metricName]: description|null } }

      // data for charts
      chartData: {},
      labels: [], // ai_model_version labels (sorted unique)
      selectedMetrics: [],

      // raw runs
      runData: [],

      // ui
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { intersect: false, mode: "nearest" },
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label(ctx) {
                // show N/A instead of null
                const v = ctx.parsed.y;
                return `${ctx.dataset.label}: ${v == null ? "N/A" : v}`;
              },
            },
          },
        },
        scales: {
          y: { beginAtZero: true },
        },
      },

      isLoading: false,
      snackbar: false,
      snackbarText: "",
      snackbarColor: "info",
    };
  },
  mounted() {
    this.configId = this.$route.params.configId;
    this.bootstrap();
  },
  methods: {
    async bootstrap() {
      this.isLoading = true;
      try {
        // Always fetch runs first (labels depend on this)
        await this.fetchRuns();

        // Outcome mode: fetch metric catalogue to build left menu
        if (!this.coreMode) {
          await this.fetchMetricGroups();
        } else {
          this.prepareCoreGroups();
        }

        // Build datasets across all runs
        await this.populateAllRuns();
      } catch (e) {
        console.error(e);
        this.showMessage("Failed to load data.", "error");
      } finally {
        this.isLoading = false;
      }
    },

    async fetchRuns() {
      const { data } = await resultService.getResultsByConfig(this.configId);
      this.runData = data || [];
      // make sorted unique labels of AI model versions
      const labels = (this.runData || [])
        .map((r) => r.ai_model_version)
        .filter(Boolean);
      this.labels = [...new Set(labels)].sort((a, b) =>
        a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" })
      );
    },

    async fetchMetricGroups() {
      // const { data } = await evaluationService.getMetrics();
      this.isLoading = true;
      evaluationService.getMetrics().then((response) => {
        this.groupedMetrics = response.data;
        // Build a group -> metricName -> description map
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
        this.selectedGroup = this.groupOptions[0].value;
        this.updateSelectedMetrics();
        this.fetchData && this.fetchData();
      });
    },

    prepareCoreGroups() {
      // left menu for core mode
      this.groupOptions = [{ title: CORE_GROUP, value: CORE_GROUP }];
      this.selectedGroup = CORE_GROUP;
      // fixed metric list for core mode
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
      if (this.coreMode) return; // core uses fixed list
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
      // create base chartData objects for each selected metric up-front
      this.selectedMetrics.forEach((metric, idx) => {
        this.chartData[metric] = {
          labels: this.labels,
          datasets: [
            {
              label: metric,
              data: new Array(this.labels.length).fill(null), // null → “gap” not zero
              fill: false,
              borderColor: this.getChartColor(idx),
              tension: 0.1,
            },
          ],
        };
      });

      // fill values from each run
      for (const run of this.runData) {
        if (!run?.id) continue;
        await this.populateRun(run);
      }

      // force reactivity
      this.chartData = { ...this.chartData };
    },

    async populateRun(run) {
      const { data } = await resultService.getResultDetail(
        this.configId,
        run.id
      );
      if (!data) return;

      // source: outcome groups or core interaction
      const source = this.coreMode
        ? data.aggregates?.interaction || {}
        : data.aggregates?.by_group || {};

      const version = run.ai_model_version;
      const idx = this.labels.indexOf(version);
      if (idx === -1) return;

      if (this.coreMode) {
        // flat metrics mapping
        this.selectedMetrics.forEach((metric) => {
          const val = source?.[metric] ?? null;
          if (metric in this.chartData)
            this.chartData[metric].datasets[0].data[idx] = val;
        });
      } else {
        // group → metric → value
        const groupBlock = source?.[this.selectedGroup] || {};
        this.selectedMetrics.forEach((metric) => {
          const v = groupBlock?.[metric];
          if (metric in this.chartData) {
            // write value or null if missing
            this.chartData[metric].datasets[0].data[idx] = v ?? null;
          }
        });
      }
    },

    // UI helpers
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
    // switching mode rebuilds left menu + charts
    coreMode() {
      this.bootstrap();
    },
    // switching group (outcome mode) refreshes metrics + charts
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
