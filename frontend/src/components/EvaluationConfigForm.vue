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
              v-model="config.metrics"
              :items="availableMetrics"
              label="Select Metrics"
              multiple
              required
            ></v-select>
            <v-textarea
              v-model="config.description"
              label="Description"
            ></v-textarea>
            <v-btn type="submit" color="primary" @click="createConfig"
              >Save Configuration</v-btn
            >
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
import evaluationConfigService from "@/services/evaluationConfigService";
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  name: "EvaluationConfigForm",
  components: {
    BaseLayout,
  },
  data() {
    return {
      config: {
        application_name: "",
        ai_model_name: "",
        metrics: [],
        description: "",
      },
      availableMetrics: [],
    };
  },
  mounted() {
    this.fetchMetrics();
  },
  methods: {
    fetchMetrics() {
      evaluationConfigService.getMetrics().then((response) => {
        this.availableMetrics = response.data.metrics;
      });
    },
    submitForm() {
      evaluationConfigService
        .createConfig(this.config)
        .then(() => {
          this.$router.push("/configs/new"); // Redirect back to the list after saving
        })
        .catch((error) => {
          console.error("There was an error saving the configuration:", error);
        });
    },
  },
};
</script>
