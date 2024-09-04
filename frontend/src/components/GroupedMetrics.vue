<template>
  <v-tabs v-model="activeTab">
    <!-- Tabs for each metric group -->
    <v-tab v-for="(metrics, groupName) in groupedMetrics" :key="groupName">
      {{ groupName }}
    </v-tab>

    <!-- Tab content for each metric group -->
    <v-tab-item v-for="(metrics, groupName) in groupedMetrics" :key="groupName">
      <v-row>
        <v-col v-for="metric in metrics" :key="metric.metric" cols="12">
          <v-card>
            <v-card-title>{{ metric.metric }}</v-card-title>
            <v-card-text>{{ metric.value }}</v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-tab-item>
  </v-tabs>
</template>
<script>
import { groupMetricsByCategory } from "@/utils/metricMappingUtil.js";

export default {
  name: "GroupedMetrics",
  props: {
    result: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      activeTab: null, // Track the active tab
    };
  },
  computed: {
    groupedMetrics() {
      return groupMetricsByCategory(this.result);
    },
  },
};
</script>
