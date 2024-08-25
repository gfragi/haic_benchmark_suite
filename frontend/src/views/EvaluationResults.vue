<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Results for {{ configName }}</h2>
      <v-data-table :headers="headers" :items="results">
        <template v-slot:[`item.actions`]="{}">
          <!-- Additional actions if needed -->
        </template>
      </v-data-table>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  components: {
    BaseLayout,
  },
  data() {
    return {
      results: [],
      configName: "",
      headers: [
        { text: "Accuracy", value: "accuracy" },
        { text: "Precision", value: "precision" },
        { text: "Recall", value: "recall" },
        { text: "Evaluation Date", value: "evaluation_date" },
      ],
    };
  },
  mounted() {
    this.fetchResults();
  },
  methods: {
    fetchResults() {
      const configId = this.$route.params.configuration_id;
      this.$http
        .get(`/evaluation/${configId}/results`)
        .then((response) => {
          this.results = response.data;
          this.configName = this.results.length
            ? this.results[0].configuration_name
            : "Unknown Configuration";
        })
        .catch((error) => {
          console.error("Error fetching evaluation results:", error);
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
