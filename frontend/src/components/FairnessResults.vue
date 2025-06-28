<template>
  <v-container>
    <!-- Chart type selector and actions -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-select
          v-model="chartType"
          :items="['bar', 'line']"
          label="Chart Type"
          dense
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedModels"
          :items="allModelNames"
          label="Filter Models"
          multiple
          dense
        />
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center">
        <v-btn color="primary" @click="downloadJSON">Export JSON</v-btn>
        <v-btn color="secondary" @click="downloadCSV" class="ml-2"
          >Export CSV</v-btn
        >
      </v-col>
    </v-row>

    <!-- Per-model cards -->
    <v-row v-for="model in filteredResults" :key="model.model" class="mb-6">
      <v-col cols="12">
        <v-card outlined>
          <v-card-title>{{ model.model }}</v-card-title>
          <v-card-text>
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  Accuracy: {{ format(model.overall.accuracy) }}
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  Selection Rate: {{ format(model.overall.selection_rate) }}
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  Demographic Parity Difference:
                  {{ format(model.demographic_parity_difference) }}
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  Equalized Odds Difference:
                  {{ format(model.equalized_odds_difference) }}
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Grouped Charts -->
    <v-row>
      <v-col cols="12">
        <h3 class="text-h6 mb-2">Accuracy by Group</h3>
        <PlotChart
          chartId="accuracy-group-chart"
          :chartData="generateChartData('accuracy')"
          :chartType="chartType"
        />
      </v-col>
      <v-col cols="12" class="mt-6">
        <h3 class="text-h6 mb-2">Selection Rate by Group</h3>
        <PlotChart
          chartId="selection-rate-group-chart"
          :chartData="generateChartData('selection_rate')"
          :chartType="chartType"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import PlotChart from "@/components/PlotChart.vue";

export default {
  name: "FairnessResults",
  components: { PlotChart },
  props: { results: Array },
  data() {
    return {
      chartType: "bar",
      selectedModels: [],
      baseColors: [
        "#4CAF50",
        "#2196F3",
        "#FFC107",
        "#E91E63",
        "#9C27B0",
        "#00BCD4",
        "#FF5722",
        "#795548",
      ],
    };
  },
  computed: {
    allModelNames() {
      return this.results.map((r) => r.model);
    },
    filteredResults() {
      return this.selectedModels.length > 0
        ? this.results.filter((r) => this.selectedModels.includes(r.model))
        : this.results;
    },
  },
  methods: {
    format(value) {
      return typeof value === "number" ? value.toFixed(4) : value;
    },
    generateChartData(metric) {
      const allGroups = new Set();
      this.filteredResults.forEach((r) =>
        Object.keys(r.by_group?.[metric] || {}).forEach((g) => allGroups.add(g))
      );
      const labels = Array.from(allGroups);

      const datasets = this.filteredResults.map((r, modelIdx) => {
        const palette = this.baseColors
          .slice(modelIdx)
          .concat(this.baseColors.slice(0, modelIdx));

        const values = labels.map((g) => r.by_group?.[metric]?.[g] ?? null);

        return {
          label: r.model,
          data: values,
          backgroundColor:
            this.chartType === "bar"
              ? labels.map((_, i) => palette[i % palette.length])
              : palette[0],
          borderColor: palette[0],
          fill: false,
        };
      });

      return { labels, datasets };
    },
    downloadJSON() {
      const blob = new Blob([JSON.stringify(this.results, null, 2)], {
        type: "application/json",
      });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "fairness_results.json";
      link.click();
    },
    downloadCSV() {
      const headers = ["Model", "Metric", "Group", "Value"];
      const rows = [];
      this.results.forEach((r) => {
        for (const metric of ["accuracy", "selection_rate"]) {
          const groupVals = r.by_group?.[metric] || {};
          for (const [group, val] of Object.entries(groupVals)) {
            rows.push([r.model, metric, group, val]);
          }
        }
      });
      const csv = [headers.join(","), ...rows.map((r) => r.join(","))].join(
        "\n"
      );
      const blob = new Blob([csv], { type: "text/csv" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "fairness_results.csv";
      link.click();
    },
  },
};
</script>

<style scoped></style>
