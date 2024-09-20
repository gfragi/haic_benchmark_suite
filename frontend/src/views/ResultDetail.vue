<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Results for Configuration ID: {{ configId }}</h2>

      <!-- List of Runs in a Table with Pagination -->
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="runHeaders"
            :items="runDates"
            v-model:page="page"
            :items-per-page="itemsPerPage"
            :items-per-page-options="[10, 20, 30]"
            class="elevation-1"
          >
            <!-- Correct v-slot usage for making the row clickable -->
            <template v-slot:item="{ item }">
              <tr @click="selectRun(item.id)" style="cursor: pointer">
                <td>{{ item.id }}</td>
                <td>{{ new Date(item.evaluation_date).toLocaleString() }}</td>
                <td>{{ item.status }}</td>
                <td>{{ item.ai_model_version }}</td>
                <td>{{ item.run_description }}</td>
                <td>
                  <v-btn @click.stop="downloadResult(item.result_link)"
                    >Download</v-btn
                  >
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>

      <!-- Pagination Controls (Optional if not using v-data-table's built-in) -->
      <v-row v-if="runDates.length > itemsPerPage">
        <v-col class="d-flex justify-center">
          <v-pagination
            v-model="page"
            :length="Math.ceil(runDates.length / itemsPerPage)"
            total-visible="7"
          ></v-pagination>
        </v-col>
      </v-row>

      <!-- Back Button -->
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
        { title: "Status", value: "status" }, // Add status column
        { title: "AI Model Version", value: "ai_model_version" }, // Add execution time column
        { title: "Description", value: "run_description" }, // Add description column
        { title: "Download Results", value: "result_link" }, // Add result download link
      ],
      page: 1, // Current page for pagination
      itemsPerPage: 10, // Number of items to display per page
    };
  },
  mounted() {
    console.log("Mounted ResultList. Config ID:", this.$route.params.configId);
    this.configId = this.$route.params.configId;
    this.fetchRunDates(); // Fetch the runs once the component is mounted
  },
  methods: {
    fetchRunDates() {
      resultService
        .getResultsByConfig(this.configId)
        .then((response) => {
          console.log("API Response Data:", response.data);
          this.runDates = response.data.map((run) => ({
            id: run.id, // Use the actual run ID from the response
            evaluation_date: run.evaluation_date, // Use the returned evaluation date
            status: run.status || "Completed", // If the status is returned #TODO: Check the actual field name
            ai_model_version: run.ai_model_version || "N/A", // If execution time is available #TODO: Check the actual field name
            run_description: run.description || "No description available", // Description of the run TODO: Check the actual field name
            result_link: run.result_minio_path, // Assuming result link is in this field TODO: Check the actual field name
          }));
          console.log("Mapped Run Dates:", this.runDates);
        })
        .catch((error) => {
          console.error("Error fetching evaluation run dates:", error);
        });
    },
    selectRun(runId) {
      console.log("Run selected:", runId); // Log the selected runId
      if (!runId) {
        console.error("Invalid run selected: runId is undefined");
        return;
      }

      // Navigate to RunDetail
      this.$router.push({
        name: "RunDetail",
        params: { configId: this.configId, runId: runId },
      });
    },
    downloadResult(resultLink) {
      // Trigger the download for the result from the link
      window.open(resultLink, "_blank");
    },
    // Navigate back to the previous page
    goBack() {
      this.$router.go(-1);
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
