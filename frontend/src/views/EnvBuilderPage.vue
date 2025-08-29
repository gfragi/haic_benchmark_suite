<script setup>
import { ref } from "vue";
import { generateConfig, listConfigs } from "@/services/configurationService";

const taskName = ref("CT Scan Diagnosis (v2)");
const taskParameters = ref({
  environment: "ct_scan",
  env_params: { steps: 30, dt: 0.1 }, // or overcooked: { layout_name: "cramped_room", horizon_s: 30, dt: 0.1 }
  baseline_s: 15,
  rt_max: 5.0,
});
const agentDefinitions = ref([
  {
    name: "RadiologistAssistant",
    modality: "text",
    capabilities: ["classify", "highlight", "summarize"],
  },
  {
    name: "VoiceSupportBot",
    modality: "audio",
    capabilities: ["speak", "respond"],
  },
]);
const profileDefinitions = ref([
  { id: "user123", role: "radiologist", skill_level: "expert" },
  { id: "user456", role: "technician", skill_level: "novice" },
]);

const lastPath = ref(null);
const configs = ref([]);

async function submit() {
  const res = await generateConfig({
    task_name: taskName.value,
    task_parameters: taskParameters.value,
    agent_definitions: agentDefinitions.value,
    profile_definitions: profileDefinitions.value,
  });
  lastPath.value = res?.path || null;
  configs.value = await listConfigs();
}
</script>

<template>
  <BaseLayout>
    <template #sidebar>
      <v-navigation-drawer permanent width="360">
        <v-toolbar flat density="comfortable" title="Env Builder" />
        <v-divider />
        <v-container>
          <v-text-field
            v-model="taskName"
            label="Task Name"
            density="comfortable"
          />
          <v-textarea
            v-model="taskParameters"
            label="Task Parameters (object)"
            :rows="6"
            auto-grow
            hint='e.g., {"environment":"ct_scan","env_params":{"steps":30,"dt":0.1},"baseline_s":15}'
          />
          <v-btn color="primary" class="mt-2" @click="submit">
            <v-icon start>mdi-content-save</v-icon> Generate Config
          </v-btn>
          <div class="text-caption mt-2" v-if="lastPath">
            <strong>Saved:</strong> {{ lastPath }}
          </div>
          <v-divider class="my-4" />
          <div class="text-subtitle-2 mb-1">Available Configs</div>
          <v-list density="compact" nav v-if="configs.length">
            <v-list-item v-for="c in configs" :key="c">
              <v-list-item-title>{{ c }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-container>
      </v-navigation-drawer>
    </template>

    <v-container>
      <v-alert type="info" variant="tonal">
        Use the sidebar to generate environment configs. Then go to
        <strong>Simulator</strong> to run them.
      </v-alert>
    </v-container>
  </BaseLayout>
</template>
