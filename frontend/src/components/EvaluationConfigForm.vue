<template>
  <v-form @submit.prevent="submitForm">
    <v-text-field
      v-model="config.application_name"
      label="Application Name"
    ></v-text-field>
    <v-text-field
      v-model="config.ai_model_name"
      label="AI Model Name"
    ></v-text-field>
    <v-select
      v-model="config.metrics"
      :items="availableMetrics"
      label="Select Metrics"
      multiple
    ></v-select>
    <v-textarea v-model="config.description" label="Description"></v-textarea>
    <v-btn type="submit" color="primary">Save Configuration</v-btn>
  </v-form>
</template>

<script>
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
      // Handle form submission
    },
  },
};
</script>
