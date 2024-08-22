<template>
  <BaseLayout>
    <v-container class="ml-auto">
      <v-card class="mx-auto my-12" max-width="600">
        <v-card-title>
          <h2 class="text-h5">Create a New Evaluation Configuration</h2>
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
              item-text="metric_name"
              item-value="metric_name"
              label="Select Metrics"
              multiple
              required
            ></v-select>
            <v-textarea
              v-model="config.description"
              label="Description"
            ></v-textarea>
            <v-btn
              :disabled="isSubmitting"
              type="submit"
              color="primary"
              @click="createConfig"
            >
              <v-progress-circular
                indeterminate
                color="white"
                size="20"
                class="mr-2"
                v-if="isSubmitting"
              ></v-progress-circular>
              Save Configuration
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
import evaluationConfigService from "@/services/configurationService";
import metricsList from "@/services/metricsList";
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  name: "ConfigurationForm",
  components: {
    BaseLayout,
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
        evaluation_status: "pending", // Default value
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
    };
  },
  mounted() {
    this.fetchMetrics();
  },
  methods: {
    fetchMetrics() {
      metricsList
        .getMetrics()
        .then((response) => {
          console.log("Fetched metrics:", response.data.metrics);
          this.availableMetrics = response.data.metrics; // Assume metrics is an array of objects with `metric_name` field
        })
        .catch((error) => {
          console.error("Error fetching metrics:", error);
        });
    },
    submitForm() {
      this.isSubmitting = true;

      // Transform the metrics array into the expected format
      const transformedMetrics = this.config.metrics.map((metric) => ({
        metric_name: metric,
      }));

      const configToSubmit = {
        ...this.config,
        metrics: transformedMetrics,
      };

      evaluationConfigService
        .createConfig(configToSubmit)
        .then(() => {
          this.$router.push("/configuration/new");
          this.$router.push("/configs");
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
