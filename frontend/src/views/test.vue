<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col cols="12" class="text-center">
          <h1>Evaluation Configurations</h1>
        </v-col>
        <v-col cols="12" class="text-right">
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
        </v-col>
        <v-btn color="primary" @click="goToNewConfig" class="ml-auto">
          New Configuration
        </v-btn>
        <v-data-table
          :headers="headers"
          :items="filteredConfigs"
          class="elevation-1"
          :items-per-page="itemsPerPage"
          :footer-props="{
            'items-per-page-options': [
              5,
              10,
              15,
              20,
              { text: 'All', value: -1 },
            ],
          }"
          :sort-by="[sortBy]"
          :sort-desc="[sortDesc]"
        >
          <!-- Scoped slots for customizing the actions column -->
          <template v-slot:[`item.evaluation_status`]="{ item }">
            <v-chip :color="getStatusColor(item.evaluation_status)" dark>
              {{ item.evaluation_status }}
            </v-chip>
          </template>
          <template v-slot:[`item.actions`]="{ item }">
            <v-btn icon color="green" text @click="confirmEvaluateConfig(item)">
              <v-icon>mdi-play-circle</v-icon>
            </v-btn>
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
          <v-card-text>
            Are you sure you want to delete this Configuration?
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="dialog = false">
              Cancel
            </v-btn>
            <v-btn color="blue darken-1" text @click="deleteConfig">
              Confirm
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="confirmDialog" max-width="500px">
        <v-card>
          <v-card-title class="headline">Run Evaluation</v-card-title>
          <v-card-text>
            Are you sure you want to run this evaluation?
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="confirmDialog = false">
              Cancel
            </v-btn>
            <v-btn color="blue darken-1" text @click="runConfirmedEvaluation">
              Confirm
            </v-btn>
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
        { title: "Application Name", key: "application_name" },
        { title: "AI Model Name", key: "ai_model_name" },
        { title: "AI Model Type", key: "ai_model_type" },
        { title: "AI Model Version", key: "ai_model_version" },
        { title: "Description", key: "description" },
        { title: "Evaluation Date Time", key: "evaluation_date" },
        { title: "Evaluation Status", key: "evaluation_status" },
        { title: "Actions", key: "actions", sortable: false },
      ],
      configs: [], // This will be fetched from the API
      dialog: false, // For the delete confirmation dialog
      confirmDialog: false, // For the evaluation confirmation dialog
      configurationToDelete: null, // Temporarily store the configuration to delete
      configToEvaluate: null, // Temporarily store the configuration to evaluate
      search: "", // For search functionality
      sortBy: "evaluation_date", // Default sorting column
      sortDesc: false, // Ascending by default
      itemsPerPage: 5, // Default items per page
    };
  },
  computed: {
    filteredConfigs() {
      if (this.search) {
        return this.configs.filter((config) =>
          Object.values(config).some((val) =>
            String(val).toLowerCase().includes(this.search.toLowerCase())
          )
        );
      }
      return this.configs;
    },
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
      this.$router.push(`/configuration/edit/${configuration.id}`);
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
    confirmEvaluateConfig(config) {
      this.configToEvaluate = config;
      this.confirmDialog = true;
    },
    runConfirmedEvaluation() {
      if (!this.configToEvaluate) return;
      evaluationConfigService
        .runEvaluation(`${this.configToEvaluate.id}`)
        .then(() => {
          this.fetchConfigs();
          this.confirmDialog = false;
          this.configToEvaluate = null;
        })
        .catch((error) => {
          console.error("Error running evaluation:", error);
        });
    },
    goToNewConfig() {
      this.$router.push("/configuration/new"); // Ensure this route is correctly configured
    },
    getStatusColor(status) {
      switch (status) {
        case "completed":
          return "green";
        case "pending":
          return "orange";
        case "failed":
          return "red";
        default:
          return "grey";
      }
    },
  },
  mounted() {
    this.fetchConfigs();
  },
};
</script>
