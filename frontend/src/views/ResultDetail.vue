<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Results for Configuration ID: {{ configId }}</h2>

      <!-- List of Runs in a Table -->
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="runHeaders"
            :items="runDates"
            class="elevation-1"
            @click:row="onRunSelected"
            hide-default-footer
          >
            <template v-slot:[`item.evaluation_date`]="{ item }">
              {{ new Date(item.evaluation_date).toLocaleString() }}
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import resultService from "@/services/resultService";

export default {
  name: "ResultList",
  components: {
    BaseLayout,
  },
  data() {
    return {
      configId: null,
      runDates: [],
      runHeaders: [
        { title: "Run ID", value: "id" },
        { title: "Evaluation Date", value: "evaluation_date" },
      ],
    };
  },
  mounted() {
    console.log("Mounted ResultList. Config ID:", this.$route.params.configId);
    this.configId = this.$route.params.configId;
    this.fetchRunDates();
  },
  methods: {
    fetchRunDates() {
      if (!this.configId) {
        console.error("Config ID is undefined.");
        return;
      }
      resultService
        .getResultsByConfig(this.configId)
        .then((response) => {
          this.runDates = response.data.map((run) => ({
            id: run.id || run.run_id, // Make sure this matches your API response
            evaluation_date: run.evaluation_date,
          }));
        })
        .catch((error) => {
          console.error("Error fetching evaluation run dates:", error);
        });
    },
    onRunSelected(item) {
      console.log("Selected item:", item); // Log the entire item for debugging

      if (!item) {
        console.error("Invalid run selected: item is undefined");
        return;
      }

      const runId = item.id || item.run_id; // Try both potential property names
      if (typeof runId === "undefined") {
        console.error(
          "Invalid run selected: item.id and item.run_id are undefined",
          item
        );
        return;
      }

      console.log(
        "Run selected:",
        runId,
        "Navigating to RunDetail with configId:",
        this.configId
      );

      resultService
        .getResultDetail(this.configId, runId)
        .then((response) => {
          console.log("Fetched Run Detail:", response.data);
          this.$router.push({
            name: "RunDetail",
            params: { configId: this.configId, runId: runId },
          });
        })
        .catch((error) => {
          console.error("Error fetching run detail:", error);
          if (error.response) {
            console.error("Response data:", error.response.data);
            console.error("Response status:", error.response.status);
          }
        });
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
