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
              <v-btn
                size="small"
                color="primary"
                rounded="xl"
                @click="viewResultDetails(item)"
              >
                View Details
              </v-btn>
              <v-btn
                size="small"
                color="secondary"
                rounded="xl"
                @click="viewConfiguration(item)"
              >
                View Configuration
              </v-btn>
              <v-btn
                size="small"
                color="info"
                rounded="xl"
                @click="viewResultPlots(item)"
              >
                View Plots
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
import configurationService from "@/services/configurationService";

export default {
  components: {
    BaseLayout,
  },
  data() {
    return {
      results: [],
      headers: [
        { title: "ID", key: "configuration_id" },
        { title: "Application Name", key: "application_name" },
        { title: "AI Model", key: "ai_model_name" },
        { title: "Prediction Accuracy", key: "prediction_accuracy" },
        { title: "Response Time", key: "response_time" },
        { title: "Teaching Efficiency", key: "teaching_efficiency" },
        { title: "Overall System Accuracy", key: "overall_system_accuracy" },
        { title: "Evaluation Date", key: "evaluation_date" },
        { title: "Actions", key: "actions", sortable: false },
      ],
    };
  },
  mounted() {
    this.fetchResults();
  },
  methods: {
    // fetchResults() {
    //   evaluationService
    //     .getAllEvaluationResults()
    //     .then((response) => {
    //       console.log("Fetched Results:", response.data); // Log to inspect the results
    //       this.results = response.data;
    //     })
    //     .catch((error) => {
    //       console.error("Error fetching evaluation results:", error);
    //     });
    // },
    viewResultDetails(item) {
      console.log("Item ID:", item.configuration_id);
      console.log("Item Object:", item);
      this.$router.push({
        name: "ResultDetail",
        params: { resultId: item.configuration_id },
      });
    },
    viewConfiguration(item) {
      configurationService
        .getConfigById(item.configuration_id)
        .then((response) => {
          this.$router.push({
            name: "ConfigurationDetail",
            params: { configId: response.data.id },
          });
        })
        .catch((error) => {
          console.error("Error fetching configuration:", error);
        });
    },
    viewResultPlots(item) {
      console.log("Item ID:", item.configuration_id);
      this.$router.push({
        name: "ResultPlot",
        params: { resultId: item.configuration_id },
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
