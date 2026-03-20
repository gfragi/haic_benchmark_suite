const { describe, it, expect, beforeEach, vi } = require("jest");
const { createApp } = require("vue");
const { createStore } = require("vuex");
const {
  useConfigurationForm,
} = require("../../src/composables/useConfigurationForm");

// Mock the store modules
const mockConfigurationModule = {
  namespaced: true,
  actions: {
    fetchConfigurationById: vi.fn(),
    createConfiguration: vi.fn(),
    updateConfiguration: vi.fn(),
  },
  getters: {
    currentConfig: vi.fn(() => null),
  },
};

const mockEvaluationModule = {
  namespaced: true,
  actions: {
    fetchMetrics: vi.fn(),
  },
  getters: {
    availableMetrics: vi.fn(() => []),
  },
};

const mockUiModule = {
  namespaced: true,
  actions: {
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showWarning: vi.fn(),
  },
};

const createMockStore = () => {
  return createStore({
    modules: {
      configuration: mockConfigurationModule,
      evaluation: mockEvaluationModule,
      ui: mockUiModule,
    },
  });
};

// Mock Vue Router
const mockRouter = {
  push: vi.fn(),
};

// Mock useRouter composable
vi.mock("vue-router", () => ({
  useRouter: () => mockRouter,
}));

describe("useConfigurationForm Composable", () => {
  let store;
  let composable;

  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();

    // Create fresh store for each test
    store = createMockStore();

    // Create a test Vue app with the store
    const app = createApp({});
    app.use(store);

    // Test props
    const props = {
      mode: "create",
      configId: null,
    };

    // Call the composable (this would normally be done in a component's setup)
    composable = useConfigurationForm(props);
  });

  describe("Initialization", () => {
    it("should initialize with default values for create mode", () => {
      expect(composable.config.value.application_name).toBe("");
      expect(composable.config.value.ai_model_name).toBe("");
      expect(composable.config.value.ai_model_type).toBe("");
      expect(composable.config.value.metrics).toEqual([]);
      expect(composable.config.value.description).toBe("");
    });

    it("should have correct computed properties", () => {
      expect(composable.isEditMode.value).toBe(false);
      expect(composable.formTitle.value).toBe(
        "Create Evaluation Configuration"
      );
      expect(composable.submitButtonText.value).toBe("Next");
    });

    it("should fetch metrics on mount", () => {
      expect(mockEvaluationModule.actions.fetchMetrics).toHaveBeenCalled();
    });

    it("should not load config for create mode", () => {
      expect(
        mockConfigurationModule.actions.fetchConfigurationById
      ).not.toHaveBeenCalled();
    });
  });

  describe("Edit Mode", () => {
    beforeEach(() => {
      const props = {
        mode: "edit",
        configId: 123,
      };
      composable = useConfigurationForm(props);
    });

    it("should load configuration for edit mode", () => {
      expect(
        mockConfigurationModule.actions.fetchConfigurationById
      ).toHaveBeenCalledWith(expect.any(Object), 123);
    });

    it("should have correct edit mode properties", () => {
      expect(composable.isEditMode.value).toBe(true);
      expect(composable.formTitle.value).toBe("Edit Evaluation Configuration");
      expect(composable.submitButtonText.value).toBe("Update");
    });
  });

  describe("Form Validation", () => {
    it("should validate required fields", () => {
      expect(composable.isFormValid.value).toBe(false);

      composable.config.value.application_name = "Test App";
      composable.config.value.ai_model_name = "Test Model";
      composable.config.value.ai_model_type = "Classification";
      composable.config.value.metrics = ["accuracy"];

      expect(composable.isFormValid.value).toBe(true);
    });

    it("should require application name", () => {
      composable.config.value.application_name = "";
      composable.config.value.ai_model_name = "Test Model";
      composable.config.value.ai_model_type = "Classification";
      composable.config.value.metrics = ["accuracy"];

      expect(composable.isFormValid.value).toBe(false);
    });

    it("should require AI model name", () => {
      composable.config.value.application_name = "Test App";
      composable.config.value.ai_model_name = "";
      composable.config.value.ai_model_type = "Classification";
      composable.config.value.metrics = ["accuracy"];

      expect(composable.isFormValid.value).toBe(false);
    });

    it("should require AI model type", () => {
      composable.config.value.application_name = "Test App";
      composable.config.value.ai_model_name = "Test Model";
      composable.config.value.ai_model_type = "";
      composable.config.value.metrics = ["accuracy"];

      expect(composable.isFormValid.value).toBe(false);
    });

    it("should require at least one metric", () => {
      composable.config.value.application_name = "Test App";
      composable.config.value.ai_model_name = "Test Model";
      composable.config.value.ai_model_type = "Classification";
      composable.config.value.metrics = [];

      expect(composable.isFormValid.value).toBe(false);
    });
  });

  describe("Form Submission", () => {
    beforeEach(() => {
      // Set up valid form data
      composable.config.value = {
        application_name: "Test App",
        ai_model_name: "Test Model",
        ai_model_type: "Classification",
        metrics: ["accuracy"],
        description: "Test description",
      };
    });

    it("should create configuration in create mode", async () => {
      const mockResponse = { id: 123, ...composable.config.value };
      mockConfigurationModule.actions.createConfiguration.mockResolvedValue(
        mockResponse
      );

      await composable.submitForm();

      expect(
        mockConfigurationModule.actions.createConfiguration
      ).toHaveBeenCalledWith(expect.any(Object), composable.config.value);
      expect(mockUiModule.actions.showSuccess).toHaveBeenCalled();
      expect(mockRouter.push).toHaveBeenCalledWith({
        path: "/logs/upload",
        query: { configId: 123 },
      });
    });

    it("should update configuration in edit mode", async () => {
      // Set up edit mode
      const props = { mode: "edit", configId: 456 };
      composable = useConfigurationForm(props);

      const mockResponse = { id: 456, ...composable.config.value };
      mockConfigurationModule.actions.updateConfiguration.mockResolvedValue(
        mockResponse
      );

      await composable.submitForm();

      expect(
        mockConfigurationModule.actions.updateConfiguration
      ).toHaveBeenCalledWith(expect.any(Object), {
        id: 456,
        configData: composable.config.value,
      });
      expect(mockUiModule.actions.showSuccess).toHaveBeenCalled();
      expect(mockRouter.push).toHaveBeenCalledWith({
        path: "/logs/upload",
        query: { configId: 456 },
      });
    });

    it("should show warning for invalid form", async () => {
      composable.config.value.application_name = ""; // Make form invalid

      await composable.submitForm();

      expect(mockUiModule.actions.showWarning).toHaveBeenCalledWith(
        "Please fill in all required fields"
      );
      expect(
        mockConfigurationModule.actions.createConfiguration
      ).not.toHaveBeenCalled();
    });

    it("should handle submission errors", async () => {
      const error = new Error("API Error");
      mockConfigurationModule.actions.createConfiguration.mockRejectedValue(
        error
      );

      await composable.submitForm();

      expect(mockUiModule.actions.showError).toHaveBeenCalledWith(
        "Failed to create configuration"
      );
    });
  });

  describe("Available Options", () => {
    it("should provide available model types", () => {
      expect(composable.availableModelTypes).toEqual([
        "Classification",
        "Regression",
        "Clustering",
        "XAI",
        "Swarm Learning",
        "Active Learning",
        "Other",
      ]);
    });

    it("should provide available config types", () => {
      expect(composable.availableConfigTypes).toEqual(["specific", "generic"]);
    });
  });
});
