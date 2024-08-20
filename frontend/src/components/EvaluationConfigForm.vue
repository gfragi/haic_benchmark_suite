<template>
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
    <v-textarea v-model="config.description" label="Description"></v-textarea>
    <v-btn type="submit" color="primary">Save Configuration</v-btn>
  </v-form>
</template>

<script>
import evaluationConfigService from "@/services/evaluationConfigService"; // Import the service

export default {
  name: "EvaluationConfigForm",
  data() {
    return {
      config: {
        application_name: "",
        ai_model_name: "",
        metrics: [],
        description: "",
      },
      availableMetrics: [
        "Prediction Accuracy",
        "Response Time",
        "Teaching Efficiency" /* Add more metrics */,
      ],
    };
  },
  methods: {
    submitForm() {
      evaluationConfigService
        .createConfig(this.config)
        .then(() => {
          this.$router.push("/configs"); // Redirect back to the list after saving
        })
        .catch((error) => {
          console.error("There was an error saving the configuration:", error);
        });
    },
  },
};
</script>
