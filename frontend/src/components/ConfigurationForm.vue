<template>
  <BaseLayout>
    <v-container class="ml-auto">
      <v-card class="mx-auto my-12" max-width="600">
        <v-card-title>
          <h2 class="text-h5">{{ formTitle }}</h2>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="submitForm">
            <v-text-field
              v-model="config.application_name"
              label="Application Name"
              required
              :rules="[(v) => !!v || 'Application name is required']"
            />
            <v-text-field
              v-model="config.ai_model_name"
              label="AI Model Name"
              required
              :rules="[(v) => !!v || 'AI model name is required']"
            />
            <v-select
              v-model="config.ai_model_type"
              :items="availableModelTypes"
              label="AI Model Type"
              required
              :rules="[(v) => !!v || 'AI model type is required']"
            />
            <v-select
              v-model="config.metrics"
              :items="availableMetrics"
              item-title="group_name"
              item-value="group_name"
              label="Select Metrics Group"
              multiple
              required
              :rules="[
                (v) =>
                  (!!v &&
                    (Array.isArray(v)
                      ? v.length > 0
                      : String(v).trim().length > 0)) ||
                  'At least one metric group is required',
              ]"
            />
            <v-textarea
              v-model="config.description"
              label="Description"
              placeholder="Optional description of this configuration"
            />
            <v-btn
              color="success"
              :disabled="isSubmitting || !isFormValid"
              @click="submitForm"
              class="justify-end"
              type="submit"
            >
              {{ submitButtonText }} Step
              <v-progress-circular
                v-if="isSubmitting"
                indeterminate
                color="white"
                size="20"
                class="ml-2"
              />
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
/**
 * ConfigurationForm Component
 *
 * A form component for creating and editing evaluation configurations.
 * Uses Vuex store for state management and a composable for form logic.
 *
 * @props {String} mode - 'create' or 'edit'
 * @props {Number} configId - Configuration ID for edit mode
 */
import BaseLayout from "@/components/BaseLayout.vue";
import { useConfigurationForm } from "@/composables/useConfigurationForm";

export default {
  name: "ConfigurationForm",
  components: {
    BaseLayout,
  },
  props: {
    mode: {
      type: String,
      default: "create",
      validator: (value) => ["create", "edit"].includes(value),
    },
    configId: {
      type: Number,
      default: null,
    },
  },
  setup(props) {
    return useConfigurationForm(props);
  },
};
</script>

<style scoped>
.v-card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.v-btn {
  min-width: 120px;
}
</style>
