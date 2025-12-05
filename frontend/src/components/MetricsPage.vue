<template>
  <BaseLayout>
    <v-container>
      <v-card class="mx-auto my-5" max-width="1200" outlined>
        <v-card-title class="text-h5">
          Human-AI Collaboration Metrics
        </v-card-title>
        <v-card-subtitle class="text-body-1 text-medium-emphasis mb-4">
          Comprehensive definitions and formulas for HAIC evaluation metrics
        </v-card-subtitle>

        <v-card-text>
          <v-expansion-panels multiple variant="accordion">
            <MetricGroup
              v-for="group in metricGroups"
              :key="group.title"
              :title="group.title"
              :icon="group.icon"
              :icon-color="group.iconColor"
              :metrics="group.metrics"
            />
          </v-expansion-panels>
        </v-card-text>

        <v-card-actions class="justify-center pb-4">
          <v-btn
            color="primary"
            variant="outlined"
            to="/"
            prepend-icon="mdi-home"
          >
            Back to Dashboard
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
/**
 * MetricsPage Component
 *
 * Displays comprehensive documentation for all HAIC metrics.
 * Uses modular MetricGroup components for better organization.
 */
import BaseLayout from "@/components/BaseLayout.vue";
import MetricGroup from "@/components/metrics/MetricGroup.vue";
import { useMetrics } from "@/composables/useMetrics";

export default {
  name: "MetricsPage",
  components: {
    BaseLayout,
    MetricGroup,
  },
  setup() {
    const { metricGroups } = useMetrics();

    return {
      metricGroups,
    };
  },
};
</script>

<style scoped>
.v-card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.v-card-title {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
  padding-bottom: 16px;
}

.v-expansion-panels {
  margin-top: 8px;
}
</style>
