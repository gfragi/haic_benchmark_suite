const { describe, it, expect } = require("jest");
const { useMetrics } = require("../../src/composables/useMetrics");

describe("useMetrics Composable", () => {
  let metricsComposable;

  beforeEach(() => {
    metricsComposable = useMetrics();
  });

  describe("Metric Groups Structure", () => {
    it("should return an array of metric groups", () => {
      expect(Array.isArray(metricsComposable.metricGroups.value)).toBe(true);
      expect(metricsComposable.metricGroups.value.length).toBeGreaterThan(0);
    });

    it("should have required properties for each group", () => {
      const firstGroup = metricsComposable.metricGroups.value[0];

      expect(firstGroup).toHaveProperty("title");
      expect(firstGroup).toHaveProperty("icon");
      expect(firstGroup).toHaveProperty("iconColor");
      expect(firstGroup).toHaveProperty("metrics");
      expect(Array.isArray(firstGroup.metrics)).toBe(true);
    });

    it("should have valid icon names", () => {
      metricsComposable.metricGroups.value.forEach((group) => {
        expect(typeof group.icon).toBe("string");
        expect(group.icon.length).toBeGreaterThan(0);
        expect(group.icon.startsWith("mdi-")).toBe(true);
      });
    });
  });

  describe("Effectiveness Metrics", () => {
    let effectivenessGroup;

    beforeEach(() => {
      effectivenessGroup = metricsComposable.metricGroups.value.find(
        (group) => group.title === "Effectiveness Metrics"
      );
    });

    it("should have effectiveness metrics group", () => {
      expect(effectivenessGroup).toBeDefined();
      expect(effectivenessGroup.icon).toBe("mdi-chart-line");
      expect(effectivenessGroup.iconColor).toBe("success");
    });

    it("should contain expected effectiveness metrics", () => {
      const metricTitles = effectivenessGroup.metrics.map((m) => m.title);

      expect(metricTitles).toContain("Prediction Accuracy");
      expect(metricTitles).toContain("Precision");
      expect(metricTitles).toContain("Recall");
      expect(metricTitles).toContain("Overall System Accuracy");
      expect(metricTitles).toContain("Model Improvement Rate");
    });

    it("should have valid metric structure", () => {
      effectivenessGroup.metrics.forEach((metric) => {
        expect(metric).toHaveProperty("title");
        expect(metric).toHaveProperty("description");
        expect(metric).toHaveProperty("formula");

        expect(typeof metric.title).toBe("string");
        expect(typeof metric.description).toBe("string");
        expect(typeof metric.formula).toBe("string");

        expect(metric.title.length).toBeGreaterThan(0);
        expect(metric.description.length).toBeGreaterThan(0);
        expect(metric.formula.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Efficiency Metrics", () => {
    let efficiencyGroup;

    beforeEach(() => {
      efficiencyGroup = metricsComposable.metricGroups.value.find(
        (group) => group.title === "Efficiency Metrics"
      );
    });

    it("should have efficiency metrics group", () => {
      expect(efficiencyGroup).toBeDefined();
      expect(efficiencyGroup.icon).toBe("mdi-timer-sand");
      expect(efficiencyGroup.iconColor).toBe("warning");
    });

    it("should contain expected efficiency metrics", () => {
      const metricTitles = efficiencyGroup.metrics.map((m) => m.title);

      expect(metricTitles).toContain("Response Time");
      expect(metricTitles).toContain("Task Completion Time");
      expect(metricTitles).toContain("Teaching Efficiency");
      expect(metricTitles).toContain("Query Efficiency");
      expect(metricTitles).toContain("Resource Utilization");
    });
  });

  describe("Adaptability and Learning Metrics", () => {
    let adaptabilityGroup;

    beforeEach(() => {
      adaptabilityGroup = metricsComposable.metricGroups.value.find(
        (group) => group.title === "Adaptability and Learning Metrics"
      );
    });

    it("should have adaptability metrics group", () => {
      expect(adaptabilityGroup).toBeDefined();
      expect(adaptabilityGroup.icon).toBe("mdi-lightbulb-on-outline");
      expect(adaptabilityGroup.iconColor).toBe("info");
    });

    it("should contain expected adaptability metrics", () => {
      const metricTitles = adaptabilityGroup.metrics.map((m) => m.title);

      expect(metricTitles).toContain("Feedback Impact");
      expect(metricTitles).toContain("Adaptability Score");
      expect(metricTitles).toContain("Impact of Corrections");
      expect(metricTitles).toContain("Learning Efficiency");
    });
  });

  describe("Collaboration and Interaction Metrics", () => {
    let collaborationGroup;

    beforeEach(() => {
      collaborationGroup = metricsComposable.metricGroups.value.find(
        (group) => group.title === "Collaboration and Interaction Metrics"
      );
    });

    it("should have collaboration metrics group", () => {
      expect(collaborationGroup).toBeDefined();
      expect(collaborationGroup.icon).toBe("mdi-account-group");
      expect(collaborationGroup.iconColor).toBe("secondary");
    });

    it("should contain expected collaboration metrics", () => {
      const metricTitles = collaborationGroup.metrics.map((m) => m.title);

      expect(metricTitles).toContain("Human-AI Agreement Rate");
      expect(metricTitles).toContain("AI Assistance Rate");
      expect(metricTitles).toContain("Decision Effectiveness");
    });
  });

  describe("Trust and Safety Metrics", () => {
    let trustGroup;

    beforeEach(() => {
      trustGroup = metricsComposable.metricGroups.value.find(
        (group) => group.title === "Trust and Safety Metrics"
      );
    });

    it("should have trust metrics group", () => {
      expect(trustGroup).toBeDefined();
      expect(trustGroup.icon).toBe("mdi-shield-check-outline");
      expect(trustGroup.iconColor).toBe("success");
    });

    it("should contain expected trust metrics", () => {
      const metricTitles = trustGroup.metrics.map((m) => m.title);

      expect(metricTitles).toContain("Confidence");
      expect(metricTitles).toContain("Trust Score");
      expect(metricTitles).toContain("Safety Incidents");
    });
  });

  describe("Robustness and Generalization Metrics", () => {
    let robustnessGroup;

    beforeEach(() => {
      robustnessGroup = metricsComposable.metricGroups.value.find(
        (group) => group.title === "Robustness and Generalization Metrics"
      );
    });

    it("should have robustness metrics group", () => {
      expect(robustnessGroup).toBeDefined();
      expect(robustnessGroup.icon).toBe("mdi-shield-alert-outline");
      expect(robustnessGroup.iconColor).toBe("error");
    });

    it("should contain expected robustness metrics", () => {
      const metricTitles = robustnessGroup.metrics.map((m) => m.title);

      expect(metricTitles).toContain("Adversarial Robustness");
      expect(metricTitles).toContain("Domain Generalization");
    });
  });

  describe("Metric Formulas", () => {
    it("should have valid mathematical formulas", () => {
      metricsComposable.metricGroups.value.forEach((group) => {
        group.metrics.forEach((metric) => {
          // Check that formulas contain mathematical operators or variables
          const hasMathElements =
            /[+\-×÷=≠≈%()]/.test(metric.formula) ||
            /[A-Za-z]+\s*[+\-×÷=≠≈%()]/.test(metric.formula) ||
            /Rate|Score|Time|Accuracy/i.test(metric.formula);

          expect(hasMathElements).toBe(true);
        });
      });
    });

    it("should have readable formula descriptions", () => {
      metricsComposable.metricGroups.value.forEach((group) => {
        group.metrics.forEach((metric) => {
          expect(metric.formula.length).toBeGreaterThan(10);
          expect(metric.formula.length).toBeLessThan(200);
        });
      });
    });
  });

  describe("Data Integrity", () => {
    it("should have no duplicate metric titles across all groups", () => {
      const allTitles = [];
      metricsComposable.metricGroups.value.forEach((group) => {
        group.metrics.forEach((metric) => {
          expect(allTitles).not.toContain(metric.title);
          allTitles.push(metric.title);
        });
      });
    });

    it("should have reasonable metric counts per group", () => {
      metricsComposable.metricGroups.value.forEach((group) => {
        expect(group.metrics.length).toBeGreaterThanOrEqual(2);
        expect(group.metrics.length).toBeLessThanOrEqual(6);
      });
    });

    it("should have non-empty descriptions", () => {
      metricsComposable.metricGroups.value.forEach((group) => {
        group.metrics.forEach((metric) => {
          expect(metric.description.trim().length).toBeGreaterThan(20);
        });
      });
    });
  });
});
