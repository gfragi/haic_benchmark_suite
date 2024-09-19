<template>
  <BaseLayout>
    <v-container class="ml-auto">
      <v-card class="mx-auto my-12" max-width="600">
        <v-card-title>
          <h2 class="text-h5">
            {{ mode === "edit" ? "Edit" : "Create" }} Evaluation Configuration
          </h2>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitForm">
            <v-text-field
              v-model="config.application_name"
              label="Application Name"
              required
            ></v-text-field>
            <v-text-field
              v-model="config.ai_model_name"
              label="AI Model Name"
              required
            ></v-text-field>
            <v-select
              v-model="config.ai_model_type"
              :items="availableModelTypes"
              label="AI Model Type"
              required
            ></v-select>
            <v-select
              v-model="config.config_type"
              :items="availableConfigTypes"
              label="Configuration Type"
              required
            ></v-select>
            <v-select
              v-model="config.metrics"
              :items="availableMetrics"
              item-title="group_name"
              item-value="group_name"
              label="Select Metrics Group"
              multiple
              required
            ></v-select>
            <v-textarea
              v-model="config.description"
              label="Description"
            ></v-textarea>
            <v-btn
              color="success"
              :disabled="isSubmitting"
              @click="submitForm"
              class="justify-end"
            >
              {{ mode === "edit" ? "Update" : "Next" }} Step
              <v-progress-circular
                v-if="isSubmitting"
                indeterminate
                color="white"
                size="20"
                class="ml-2"
              ></v-progress-circular>
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
import configurationService from "@/services/configurationService";
import metricsList from "@/services/evaluationService";
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  name: "ConfigurationForm",
  components: {
    BaseLayout,
  },
  props: {
    mode: {
      type: String,
      default: "create", // Can be 'create' or 'edit'
    },
    configId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      config: {
        application_name: "",
        ai_model_name: "",
        ai_model_type: "",
        metrics: [],
        description: "",
        config_type: "",
        evaluation_status: "pending",
        evaluation_date: new Date().toISOString(),
      },
      availableMetrics: [],
      availableModelTypes: [
        "Classification",
        "Regression",
        "Clustering",
        "XAI",
        "Swarm Learning",
        "Active Learning",
        "Other",
      ],
      availableConfigTypes: ["specific", "generic"],
      isSubmitting: false,
    };
  },
  mounted() {
    this.fetchMetrics();
    if (this.mode === "edit" && this.configId) {
      this.loadConfig();
    }
  },
  methods: {
    fetchMetrics() {
      metricsList
        .getMetrics()
        .then((response) => {
          const metricGroups = Object.keys(response.data);
          this.availableMetrics = metricGroups.map((group) => ({
            group_name: group,
            metrics: response.data[group].metrics,
          }));
        })
        .catch((error) => {
          console.error("Error fetching metrics:", error);
        });
    },
    loadConfig() {
      configurationService
        .getConfigById(this.configId)
        .then((response) => {
          this.config = { ...response.data };
        })
        .catch((error) => {
          console.error("Error loading configuration:", error);
        });
    },
    submitForm() {
      this.isSubmitting = true;
      const serviceCall =
        this.mode === "edit"
          ? configurationService.updateConfig(this.configId, this.config)
          : configurationService.createConfig(this.config);

      serviceCall
        .then((response) => {
          const configId = response.data.id;
          this.$router.push({ path: "/logs/upload", query: { configId } });
        })
        .catch((error) => {
          console.error("Error while submitting form:", error);
        })
        .finally(() => {
          this.isSubmitting = false;
        });
    },
  },
};
</script>
