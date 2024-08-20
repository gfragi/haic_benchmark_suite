<template>
  <v-app-bar app color="primary" dark>
    <v-btn icon @click="$emit('toggleSidebar')">
      <v-icon>mdi-menu</v-icon>
    </v-btn>
    <v-toolbar-title>HAIC Evaluation Platform</v-toolbar-title>
  </v-app-bar>
</template>

<script>
export default {
  name: "HeaderComponent",
};
</script>
