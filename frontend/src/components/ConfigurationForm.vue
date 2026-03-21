<template>
  <BaseLayout>
    <v-container class="ml-auto">
      <!-- ── FIRST-RUN WIZARD (shown after successful submit) ──────── -->
      <v-card v-if="showWizard" class="mx-auto my-12" max-width="620">
        <v-card-title class="d-flex align-center ga-2 pt-5 pb-3 px-6">
          <v-icon color="success" size="28">mdi-check-circle</v-icon>
          <span class="text-h6">Configuration Created!</span>
        </v-card-title>

        <v-divider />

        <v-card-text class="px-6 pt-5">
          <p class="text-body-1 mb-6 text-medium-emphasis">
            Follow these three steps to run your first evaluation and see
            results.
          </p>

          <!-- Step 1 — Complete -->
          <div class="wizard-step d-flex align-start ga-4 mb-5">
            <v-icon
              color="success"
              size="32"
              style="flex-shrink: 0; margin-top: 2px"
            >
              mdi-check-circle
            </v-icon>
            <div>
              <p class="text-subtitle-1 font-weight-medium mb-0">
                Configuration created
              </p>
              <p class="text-caption text-medium-emphasis">
                Your evaluation setup is saved and ready to use.
              </p>
            </div>
          </div>

          <!-- Connector line -->
          <div class="wizard-connector mb-5" />

          <!-- Step 2 — Current -->
          <div class="wizard-step d-flex align-start ga-4 mb-5">
            <v-icon
              color="primary"
              size="32"
              style="flex-shrink: 0; margin-top: 2px"
            >
              mdi-numeric-2-circle
            </v-icon>
            <div>
              <p class="text-subtitle-1 font-weight-medium mb-1">
                Upload or register a log file
              </p>
              <p class="text-caption text-medium-emphasis mb-3">
                Provide the interaction log that records human-AI activity to
                evaluate.
              </p>
              <v-btn
                color="primary"
                variant="tonal"
                size="small"
                rounded="lg"
                to="/logs/upload"
              >
                <v-icon start>mdi-upload</v-icon>
                Upload Log
              </v-btn>
            </div>
          </div>

          <!-- Connector line -->
          <div class="wizard-connector mb-5" />

          <!-- Step 3 — Pending -->
          <div class="wizard-step d-flex align-start ga-4">
            <v-icon
              color="blue-grey-lighten-3"
              size="32"
              style="flex-shrink: 0; margin-top: 2px"
            >
              mdi-numeric-3-circle-outline
            </v-icon>
            <div>
              <p class="text-subtitle-1 font-weight-medium mb-1 text-disabled">
                Run evaluation to see results
              </p>
              <p class="text-caption text-medium-emphasis">
                Once your log is uploaded, trigger the evaluation engine to
                compute Trust, Cognitive Load, Adaptability, and other HAIC
                metrics.
              </p>
            </div>
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions class="px-6 py-4">
          <v-btn variant="text" @click="showWizard = false">
            <v-icon start>mdi-arrow-left</v-icon>
            Back to form
          </v-btn>
          <v-spacer />
          <v-btn
            variant="outlined"
            color="secondary"
            rounded="lg"
            to="/configs"
          >
            <v-icon start>mdi-view-list</v-icon>
            All Configurations
          </v-btn>
        </v-card-actions>
      </v-card>

      <!-- ── CONFIGURATION FORM (hidden once wizard is shown) ────────── -->
      <v-card v-else class="mx-auto my-12" max-width="600">
        <v-card-title>
          <h2 class="text-h5">{{ formTitle }}</h2>
        </v-card-title>
        <v-card-text>
          <v-form @submit.prevent="handleSubmit">
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
              @click="handleSubmit"
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

  data() {
    return {
      // Wizard state — shown after a successful create submission
      showWizard: false,
      isSubmitting: false,
    };
  },

  methods: {
    /**
     * Wraps the composable's submitForm so we can show the
     * first-run wizard after a successful creation.
     */
    async handleSubmit() {
      this.isSubmitting = true;
      try {
        await this.submitForm();
        // Only show the wizard when creating (not editing)
        if (this.mode === "create") {
          this.showWizard = true;
        }
      } catch (err) {
        console.error("Configuration submit failed:", err);
      } finally {
        this.isSubmitting = false;
      }
    },
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

/* Vertical connector line between wizard steps */
.wizard-connector {
  width: 2px;
  height: 24px;
  background-color: #e0e0e0;
  margin-left: 15px; /* aligns under the centre of the 32px icon */
}
</style>
