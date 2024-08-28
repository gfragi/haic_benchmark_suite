<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Result Details</h2>
      <v-row v-if="results.length">
        <v-col v-for="(result, index) in results" :key="index" cols="12">
          <v-card>
            <v-card-title>
              Result {{ index + 1 }} - Configuration ID:
              {{ result.configuration_id }}
            </v-card-title>
            <v-card-subtitle>
              Evaluation Date:
              {{ new Date(result.evaluation_date).toLocaleString() }}
            </v-card-subtitle>
            <v-card-text>
              <v-data-table
                :headers="metricHeaders"
                :items="getMetrics(result)"
                class="elevation-1"
              >
                <template v-slot:[`item.metric`]="{ item }">
                  {{ item.metric }}
                </template>
                <template v-slot:[`item.value`]="{ item }">
                  {{ item.value }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-else>
        <v-col cols="12">
          <p>No results available.</p>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationService from "@/services/resultService";

export default {
  components: {
    BaseLayout,
  },
  data() {
    return {
      results: [], // Should be 'results' not 'result'
      metricHeaders: [
        { text: "Metric", value: "metric" },
        { text: "Value", value: "value" },
      ],
    };
  },
  mounted() {
    this.fetchResultDetail();
  },
  methods: {
    fetchResultDetail() {
      const resultId = this.$route.params.resultId;
      evaluationService
        .getEvaluationResultsByConfig(resultId)
        .then((response) => {
          this.results = response.data;
          console.log("Fetched Results: ", this.results); // Log the results to see their structure
        })
        .catch((error) => {
          console.error("Error fetching evaluation result detail:", error);
        });
    },
    getMetrics(result) {
      // Exclude properties that are not metrics
      const excludedKeys = ["id", "configuration_id", "evaluation_date"];
      return Object.keys(result)
        .filter((key) => !excludedKeys.includes(key))
        .map((key) => ({
          metric: key.replace(/_/g, " ").toUpperCase(), // Optional: Format the metric names
          value: result[key],
        }));
    },
  },
};
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
}
.v-list-item-title {
  font-weight: bold;
}
</style>
