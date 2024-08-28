<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col>
          <h2>All Evaluation Results</h2>
          <v-data-table :headers="headers" :items="results" class="elevation-1">
            <template v-slot:[`item.evaluation_date`]="{ item }">
              {{ new Date(item.evaluation_date).toLocaleString() }}
            </template>
            <template v-slot:[`item.actions`]="{ item }">
              <v-btn color="primary" @click="viewResultDetails(item)">
                View Details
              </v-btn>
            </template>
          </v-data-table>
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
      results: [],
      headers: [
        { text: "Configuration ID", value: "configuration_id" },
        { text: "Prediction Accuracy", value: "prediction_accuracy" },
        { text: "Response Time", value: "response_time" },
        { text: "Teaching Efficiency", value: "teaching_efficiency" },
        { text: "Overall System Accuracy", value: "overall_system_accuracy" },
        { text: "Evaluation Date", value: "evaluation_date" },
        { text: "Actions", value: "actions", sortable: false },
      ],
    };
  },
  mounted() {
    this.fetchResults();
  },
  methods: {
    fetchResults() {
      evaluationService
        .getAllEvaluationResults()
        .then((response) => {
          this.results = response.data;
        })
        .catch((error) => {
          console.error("Error fetching evaluation results:", error);
        });
    },
    viewResultDetails(item) {
      this.$router.push({
        name: "ResultDetail",
        params: { resultId: item.id },
      });
    },
  },
};
</script>

<style scoped>
.subtitle-1 {
  margin-top: 25px;
  color: #757575;
}
</style>
