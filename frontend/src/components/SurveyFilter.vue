<template>
  <v-select
    v-model="selected"
    :items="options"
    label="Select Pilot Tag"
    @update:modelValue="emitChange"
  />
</template>

<script setup>
import { ref } from "vue";
import { defineEmits } from "vue";

const selected = ref(null);
const options = [
  "SmartTicketing",
  "SmartEnergy",
  "Healthcare",
  "Manufacturing",
];

const emit = defineEmits(["update:pilotTag"]);

function emitChange(value) {
  emit("update:pilotTag", value);
}
</script>
