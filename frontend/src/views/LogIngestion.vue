<template>
  <v-container>
    <LogIngestionForm />
  </v-container>
</template>

<script>
import LogIngestionForm from "@/components/LogIngestionForm.vue";

export default {
  name: "LogIngestion",
  components: { LogIngestionForm },
};
</script>
