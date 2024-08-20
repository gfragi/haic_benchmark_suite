<template>
  <v-form @submit.prevent="submitLog">
    <v-file-input v-model="logFile" label="Upload Log File"></v-file-input>
    <v-btn type="submit" color="primary">Submit Log</v-btn>
  </v-form>
</template>

<script>
export default {
  name: "LogIngestionForm",
  data() {
    return {
      logFile: null,
    };
  },
  methods: {
    submitLog() {
      // Handle log submission
    },
  },
};
</script>
