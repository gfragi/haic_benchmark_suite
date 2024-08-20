<template>
  <BaseLayout>
    <!-- <v-container
      class="d-flex flex-column justify-center align-center"
      style="height: 100vh"
    > -->
    <v-card max-width="500" class="mx-auto">
      <v-card-title>
        <h2 class="text-h5">Log Ingestion</h2>
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="submitLog">
          <v-file-input
            v-model="logFile"
            label="Upload Log File"
            prepend-icon="mdi-paperclip"
            accept=".json"
            required
          ></v-file-input>
          <v-btn type="submit" color="primary" block class="mt-3">
            Submit Log
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
    <!-- </v-container> -->
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import logIngestionService from "@/services/logIngestionService";

export default {
  name: "LogIngestionForm",
  components: {
    BaseLayout,
  },
  data() {
    return {
      logFile: null,
    };
  },
  methods: {
    submitLog() {
      logIngestionService
        .uploadLog(this.logFile)
        .then(() => {
          this.$router.push({ name: "Home" });
        })
        .catch((error) => {
          console.error(error);
        });
    },
  },
};
</script>

<style scoped>
.mx-auto {
  margin-left: auto;
  margin-right: auto;
}
</style>
