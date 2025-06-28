<template>
  <v-select
    v-model="selected"
    :items="options"
    label="Select Pilot Tag"
    @change="$emit('update:pilotTag', selected)"
  />
</template>

<script setup>
import { ref, defineEmits } from "vue";
const options = ["SmartTicketing", "SmartEnergy", "Healthcare"];
const selected = ref(null);
defineEmits(["update:pilotTag"]);
</script>
