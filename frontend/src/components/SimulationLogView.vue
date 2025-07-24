<template>
  <v-data-table
    :headers="[
      { text: 'Step', value: 'step' },
      { text: 'Agent', value: 'agent' },
      { text: 'Action', value: 'action' },
    ]"
    :items="decisions"
    dense
  />
</template>

<script>
export default {
  name: "SimulationLogView",
  props: {
    decisions: Array,
  },
};
</script>
