<template>
  <BaseLayout>
    <v-container>
      <v-card class="mx-auto my-12" max-width="600">
        <v-card-title>
          <span class="headline"
            >Upload Log File for Configuration: {{ configurationName }}</span
          >
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitLog">
            <v-file-input
              v-model="file"
              label="Select log file"
              required
            ></v-file-input>
            <v-btn :disabled="!file" color="primary" type="submit">
              Upload Log
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>

    <!-- Snackbar for confirmation message -->
    <v-snackbar v-model="showSnackbar" :timeout="3000" color="success" right>
      Log file successfully uploaded!
      <v-btn color="white" text @click="showSnackbar = false">Close</v-btn>
    </v-snackbar>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import logService from "@/services/loService";
import evaluationConfigService from "@/services/configurationService";

export default {
  components: {
    BaseLayout,
  },
  data() {
    return {
      file: null,
      configId: this.$route.query.configId,
      configurationName: "",
      showSnackbar: false, // Controls the visibility of the snackbar
    };
  },
  async mounted() {
    await this.fetchConfigurationDetails();
  },
  methods: {
    async fetchConfigurationDetails() {
      try {
        const response = await evaluationConfigService.getConfigById(
          this.configId
        );
        if (response.data) {
          this.configurationName = `${response.data.application_name} - ${response.data.ai_model_name}`;
        } else {
          console.error("Configuration not found");
        }
      } catch (error) {
        console.error("Error fetching configuration details:", error);
      }
    },
    submitLog() {
      if (!this.file) {
        console.error("No file selected");
        return;
      }
      const formData = new FormData();
      formData.append("file", this.file);

      logService
        .uploadLog(formData, this.configId)
        .then(() => {
          this.showSnackbar = true; // Show the snackbar confirmation
          setTimeout(() => {
            this.$router.push("/configs"); // Redirect after showing confirmation
          }, 5000); // Redirect after the snackbar disappears
        })
        .catch((error) => {
          console.error("Failed to upload file:", error);
        });
    },
  },
};
</script>
