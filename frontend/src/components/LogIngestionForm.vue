<template>
  <BaseLayout>
    <v-container>
      <v-card class="mx-auto my-12" max-width="600">
        <v-card-title>
          <span class="headline">Upload Log File</span>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitForm">
            <v-select
              v-model="selectedConfigId"
              :items="configurations"
              item-text="name"
              item-value="id"
              label="Select Configuration"
              return-object
              required
            ></v-select>
            <v-file-input
              v-model="file"
              label="File input"
              required
            ></v-file-input>
            <v-btn
              :disabled="!file"
              color="primary"
              type="submit"
            >
              Upload
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from '@/components/BaseLayout.vue';
import evaluationConfigService from '@/services/evaluationConfigService';

export default {
  name: 'LogUploadForm',
  components: {
    BaseLayout
  },
  data() {
    return {
      configurations: [],
      selectedConfigId: null,
      file: null
    };
  },
  mounted() {
    this.fetchConfigurations();
  },
  methods: {
    fetchConfigurations() {
      evaluationConfigService.getConfigurations()
        .then(response => {
          this.configurations = response.data.map(config => ({
            id: config.id,
            name: `${config.application_name} - ${config.ai_model_name}`
          }));
        })
        .catch(error => console.error("Error fetching configurations:", error));
    },
    submitForm() {
      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('configuration_id', this.selectedConfigId);

      // Replace with your service method for uploading the file
      evaluationConfigService.uploadLog(formData)
        .then(() => {
          this.$router.push('/'); // Redirect or show success message
        })
        .catch(error => {
          console.error("Failed to upload file:", error);
        });
    }
  }
};
</script>

<style scoped>
/* Add your styles here */
</style>
