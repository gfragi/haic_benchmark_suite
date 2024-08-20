<template>
  <v-container>
    <v-form @submit.prevent="generateReport">
      <v-select
        v-model="selectedConfig"
        :items="configs"
        label="Select Configuration"
      ></v-select>
      <v-date-picker v-model="reportDate" label="Select Date"></v-date-picker>
      <v-btn type="submit" color="primary">Generate Report</v-btn>
    </v-form>
  </v-container>
</template>

<script>
export default {
  name: "EvaluationReports",
  data() {
    return {
      selectedConfig: null,
      configs: [], // Fetch available configurations
      reportDate: null,
    };
  },
  methods: {
    // generateReport() {
    //   // Call API to generate report and download it
    // }
  },
};
</script>
