<template>
  <BaseLayout>
    <v-container>
      <h2>Evaluation Results for Configuration ID: {{ configId }}</h2>

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
            <template v-slot:item="{ item }">
              <tr @click="selectRun(item.id)" style="cursor: pointer">
                <td>{{ item.id }}</td>
                <td>{{ new Date(item.evaluation_date).toLocaleString() }}</td>
                <td>{{ item.status }}</td>
                <td>{{ item.ai_model_version }}</td>
                <td>{{ item.run_description }}</td>
                <td>
                  <v-btn
                    size="small"
                    @click.stop="downloadResult(item.result_link)"
                  >
                    Download
                  </v-btn>
                </td>
              </tr>
            </template>
          </v-data-table>
        </v-col>
      </v-row>

      <v-row v-if="runDates.length > itemsPerPage">
        <v-col class="d-flex justify-center">
          <v-pagination
            v-model="page"
            :length="Math.ceil(runDates.length / itemsPerPage)"
            total-visible="7"
          />
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
import resultService from "@/services/resultService";

export default {
  name: "ResultList",
  components: { BaseLayout },
  data() {
    return {
      configId: null,
      runDates: [],
      runHeaders: [
        { title: "Run ID", value: "id" },
        { title: "Evaluation Date", value: "evaluation_date" },
        { title: "Status", value: "status" },
        { title: "AI Model Version", value: "ai_model_version" },
        { title: "Description", value: "run_description" },
        { title: "Download Results", value: "result_link" },
      ],
      page: 1,
      itemsPerPage: 10,
    };
  },
  mounted() {
    this.configId = this.$route.params.configId;
    this.fetchRunDates();
  },
  methods: {
    fetchRunDates() {
      resultService
        .getResultsByConfig(this.configId)
        .then(({ data }) => {
          this.runDates = data.map((run) => ({
            id: run.id,
            evaluation_date: run.evaluation_date,
            status: run.status || "Completed",
            ai_model_version: run.ai_model_version || "N/A",
            run_description: run.description || "No description available",
            result_link: run.result_minio_path,
          }));
        })
        .catch((err) =>
          console.error("Error fetching evaluation run dates:", err)
        );
    },
    selectRun(runId) {
      if (!runId) return;
      this.$router.push({
        name: "RunDetail",
        params: { configId: this.configId, runId },
      });
    },
    downloadResult(resultLink) {
      if (!resultLink) return;
      window.open(resultLink, "_blank");
    },
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
