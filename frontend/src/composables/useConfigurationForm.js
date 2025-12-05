// Composable for configuration form logic
import { ref, reactive, onMounted, computed } from "vue";
import { useStore } from "vuex";
import { useRouter } from "vue-router";

export function useConfigurationForm(props) {
  const store = useStore();
  const router = useRouter();

  // Form state
  const config = reactive({
    application_name: "",
    ai_model_name: "",
    ai_model_type: "",
    metrics: [],
    description: "",
    config_type: "",
    evaluation_status: "pending",
    evaluation_date: new Date().toISOString(),
  });

  // UI state
  const isSubmitting = ref(false);
  const availableMetrics = ref([]);
  const availableModelTypes = [
    "Classification",
    "Regression",
    "Clustering",
    "XAI",
    "Swarm Learning",
    "Active Learning",
    "Other",
  ];
  const availableConfigTypes = ["specific", "generic"];

  // Computed properties
  const isEditMode = computed(() => props.mode === "edit");
  const formTitle = computed(() =>
    isEditMode.value
      ? "Edit Evaluation Configuration"
      : "Create Evaluation Configuration"
  );
  const submitButtonText = computed(() =>
    isEditMode.value ? "Update" : "Next"
  );

  // Validation
  const isFormValid = computed(() => {
    return (
      config.application_name.trim() &&
      config.ai_model_name.trim() &&
      config.ai_model_type &&
      config.metrics.length > 0
    );
  });

  // Methods
  const fetchMetrics = async () => {
    try {
      // Use the evaluation store to fetch metrics
      await store.dispatch("evaluation/fetchMetrics");
      const metrics = store.getters["evaluation/availableMetrics"];

      if (metrics && typeof metrics === "object") {
        const metricGroups = Object.keys(metrics);
        availableMetrics.value = metricGroups.map((group) => ({
          group_name: group,
          metrics: metrics[group].metrics || [],
        }));
      }
    } catch (error) {
      console.error("Error fetching metrics:", error);
      store.dispatch("ui/showError", "Failed to load available metrics");
    }
  };

  const loadConfig = async () => {
    if (!isEditMode.value || !props.configId) return;

    try {
      await store.dispatch(
        "configuration/fetchConfigurationById",
        props.configId
      );
      const loadedConfig = store.getters["configuration/currentConfig"];

      if (loadedConfig) {
        Object.assign(config, loadedConfig);
      }
    } catch (error) {
      console.error("Error loading configuration:", error);
      store.dispatch("ui/showError", "Failed to load configuration");
    }
  };

  const submitForm = async () => {
    if (!isFormValid.value) {
      store.dispatch("ui/showWarning", "Please fill in all required fields");
      return;
    }

    isSubmitting.value = true;

    try {
      let response;
      if (isEditMode.value) {
        response = await store.dispatch("configuration/updateConfiguration", {
          id: props.configId,
          configData: config,
        });
      } else {
        response = await store.dispatch(
          "configuration/createConfiguration",
          config
        );
      }

      store.dispatch(
        "ui/showSuccess",
        `Configuration ${isEditMode.value ? "updated" : "created"} successfully`
      );

      // Navigate to log upload with the config ID
      const configId = response.id || response.data?.id || props.configId;
      router.push({ path: "/logs/upload", query: { configId } });
    } catch (error) {
      console.error("Error submitting form:", error);
      store.dispatch(
        "ui/showError",
        `Failed to ${isEditMode.value ? "update" : "create"} configuration`
      );
    } finally {
      isSubmitting.value = false;
    }
  };

  // Lifecycle
  onMounted(() => {
    fetchMetrics();
    loadConfig();
  });

  return {
    // State
    config,
    isSubmitting,
    availableMetrics,
    availableModelTypes,
    availableConfigTypes,

    // Computed
    isEditMode,
    formTitle,
    submitButtonText,
    isFormValid,

    // Methods
    submitForm,
  };
}
