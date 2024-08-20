<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col cols="12" class="text-center">
          <h1>Evaluation Configurations</h1>
        </v-col>
        <v-btn color="primary" @click="goToNewConfig" class="ml-auto"
          >New Configuration</v-btn
        >
        <v-data-table
          :headers="headers"
          :items="configs"
          class="elevation-1"
          :items-per-page="5"
        >
          <!-- Scoped slots for customizing the actions column -->
          <template v-slot:[`item.actions`]="{ item }">
            <v-btn icon @click="editConfig(item)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon color="red" @click="deleteConfig(item)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationConfigService from "@/services/evaluationConfigService";

export default {
  name: "EvaluationConfigList",
  components: {
    BaseLayout,
  },
  data() {
    return {
      headers: [
        { text: "Application Name", value: "application_name" },
        { text: "AI Model Name", value: "ai_model_name" },
        { text: "Description", value: "description" },
        { text: "Evaluation Date", value: "evaluation_date" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      configs: [], // This will be fetched from the API
    };
  },
  methods: {
    fetchConfigs() {
      evaluationConfigService
        .getAllConfigs()
        .then((response) => {
          this.configs = response.data;
        })
        .catch((error) => {
          console.error("Error fetching configs:", error);
        });
    },
    editConfig(config) {
      this.$router.push(`/configs/${config.id}/edit`);
    },
    deleteConfig(config) {
      evaluationConfigService.deleteConfig(config.id).then(() => {
        this.fetchConfigs(); // Refresh the list after deletion
      });
    },
    goToNewConfig() {
      this.$router.push("/configs/new"); // Ensure this route is correctly configured
    },
  },
  mounted() {
    this.fetchConfigs();
  },
};
</script>
