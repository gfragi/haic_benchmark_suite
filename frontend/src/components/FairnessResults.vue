<template>
  <v-container>
    <!-- Chart type selector -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-select
          v-model="chartType"
          :items="['bar', 'line']"
          label="Chart Type"
          dense
        />
      </v-col>
    </v-row>

    <!-- Per-model cards -->
    <v-row v-for="model in results" :key="model.model" class="mb-6">
      <v-col cols="12">
        <v-card outlined>
          <v-card-title>{{ model.model }}</v-card-title>
          <v-card-text>
            <!-- Overall Metrics -->
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
    };
  },
  methods: {
    format(value) {
      return typeof value === "number" ? value.toFixed(4) : value;
    },
    generateChartData(metric) {
      const allGroups = new Set();
      this.results.forEach((r) =>
        Object.keys(r.by_group?.[metric] || {}).forEach((g) => allGroups.add(g))
      );
      const labels = Array.from(allGroups);
      const datasets = this.results.map((r) => ({
        label: r.model,
        data: labels.map((g) => r.by_group?.[metric]?.[g] ?? null),
        backgroundColor: metric === "accuracy" ? "#42A5F5" : "#FF6384",
      }));

      return { labels, datasets };
    },
  },
};
</script>

<style scoped></style>
