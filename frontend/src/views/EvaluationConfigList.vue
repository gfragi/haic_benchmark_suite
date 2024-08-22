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
            <v-btn icon color="red" @click="confirmDeleteConfig(item)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-row>
      <v-dialog v-model="dialog" max-width="500px">
        <v-card>
          <v-card-title class="headline">Confirm Delete</v-card-title>
          <v-card-text
            >Are you sure you want to delete this Configuration?</v-card-text
          >
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="dialog = false"
              >Cancel</v-btn
            >
            <v-btn color="blue darken-1" text @click="deleteConfig"
              >Confirm</v-btn
            >
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationConfigService from "@/services/configurationService";

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
        { text: "AI Model Type", value: "ai_model_type" },
        { text: "AI Model Version", value: "ai_model_version" },
        { text: "Description", value: "description" },
        { text: "Evaluation Date", value: "evaluation_date" },
        { text: "Evaluation Status", value: "evaluation_status" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      configs: [], // This will be fetched from the API
      dialog: false, // For the delete confirmation dialog
      configurationToDelete: null, // Temporarily store the configuration to delete
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
    editConfig(configuration) {
      this.$router.push(`/configuration/${configuration.id}`);
    },
    confirmDeleteConfig(configuration) {
      this.configurationToDelete = configuration;
      this.dialog = true;
    },
    deleteConfig() {
      if (!this.configurationToDelete) return;
      evaluationConfigService
        .deleteConfig(this.configurationToDelete.id)
        .then(() => {
          this.fetchConfigs(); // Refresh the list after deletion
          this.dialog = false;
          this.configurationToDelete = null; // Clear the temp storage
        })
        .catch((error) => {
          console.error("Error deleting configuration:", error);
        });
    },
    goToNewConfig() {
      this.$router.push("/configuration/new"); // Ensure this route is correctly configured
    },
  },

  mounted() {
    this.fetchConfigs();
  },
};
</script>
