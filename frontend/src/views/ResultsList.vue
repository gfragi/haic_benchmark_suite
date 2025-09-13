<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col>
          <h2>All Evaluation Results</h2>

          <v-data-table :headers="headers" :items="results" class="elevation-1">
            <!-- Safe date rendering -->
            <template v-slot:[`item.evaluation_date`]="{ item }">
              {{ formatDate(item?.raw?.evaluation_date) }}
            </template>

            <!-- Actions: always pass the raw row -->
            <template v-slot:[`item.actions`]="{ item }">
              <v-btn
                size="small"
                color="primary"
                rounded="xl"
                @click="viewResultDetails(item.raw)"
              >
                View Details
              </v-btn>
              <v-btn
                size="small"
                color="secondary"
                rounded="xl"
                @click="viewConfiguration(item.raw)"
              >
                View Configuration
              </v-btn>
              <v-btn
                size="small"
                color="info"
                rounded="xl"
                @click="viewResultPlots(item.raw)"
              >
                View Plots
              </v-btn>
            </template>
          </v-data-table>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" class="text-center">
          <v-btn color="primary" @click="goBack">Back</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import configurationService from "@/services/configurationService";
// import evaluationService from "@/services/evaluationService"; // if you fetch results here

export default {
  components: { BaseLayout },
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
    // Make sure the objects you push into `results`
    // have the keys used in the headers (incl. evaluation_date).
    async fetchResults() {
      try {
        // example: if you previously fetched from evaluationService
        // const { data } = await evaluationService.getAllEvaluationResults();
        // this.results = data || [];
        // If `results` are provided via parent/route, keep this empty or remove
      } catch (e) {
        console.error("Error fetching evaluation results:", e);
      }
    },

    // Expect a plain row object (not the Vuetify slot wrapper)
    viewResultDetails(row) {
      this.$router.push({
        name: "ResultDetail",
        params: { configId: row.configuration_id }, // <-- uses configId
      });
    },
    async viewConfiguration(row) {
      try {
        const { data } = await configurationService.getConfigById(
          row.configuration_id
        );
        this.$router.push({
          name: "ConfigurationDetail",
          params: { configId: data.id },
        });
      } catch (e) {
        console.error("Error fetching configuration:", e);
      }
    },
    viewResultPlots(row) {
      this.$router.push({
        name: "ResultPlot",
        params: { resultId: row.configuration_id },
      });
    },

    formatDate(value) {
      if (!value) return "—";
      const d = new Date(value);
      return isNaN(d) ? String(value) : d.toLocaleString();
    },

    goBack() {
      this.$router.go(-1);
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
