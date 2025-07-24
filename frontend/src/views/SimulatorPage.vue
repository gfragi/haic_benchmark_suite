<template>
  <BaseLayout>
    <v-container>
      <h2 class="mb-4">Run Simulation</h2>

      <v-select
        v-model="selectedConfig"
        :items="configs"
        label="Select Configuration"
        item-text="name"
        item-value="name"
        class="mb-4"
      />

      <v-btn @click="runSimulation" :disabled="!selectedConfig" color="primary">
        Run Simulation
      </v-btn>

      <div v-if="result" class="mt-6">
        <h3 class="text-h6">Simulation Metrics</h3>
        <SimulationMetricsChart :metrics="result.metrics" class="mb-6" />

        <h3 class="text-h6">Agent Decisions</h3>
        <SimulationLogView :decisions="result.decisions" class="mb-4" />

        <p><strong>Log Path:</strong> {{ result.log_path }}</p>
        <v-btn @click="downloadLog" color="secondary">Download JSON</v-btn>
      </div>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import { ref, onMounted } from "vue";
import BaseLayout from "@/components/BaseLayout.vue";
import SimulationMetricsChart from "@/components/SimulationMetricsChart.vue";
import SimulationLogView from "@/components/SimulationLogView.vue";
import { fetchConfigs, simulateConfig } from "@/services/simulationService";

const configs = ref([]);
const selectedConfig = ref(null);
const result = ref(null);

onMounted(async () => {
  configs.value = await fetchConfigs();
});

const runSimulation = async () => {
  result.value = await simulateConfig(selectedConfig.value);
};

const downloadLog = () => {
  const blob = new Blob([JSON.stringify(result.value, null, 2)], {
    type: "application/json",
  });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${selectedConfig.value}_result.json`;
  link.click();
};
</script>
