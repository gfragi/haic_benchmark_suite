<template>
  <v-app-bar app color="primary" dark>
    <v-toolbar-title>HAIC Evaluation Platform</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn text to="/">Home</v-btn>
    <v-btn text to="/configs">Configurations</v-btn>
    <v-btn text to="/logs">Log Ingestion</v-btn>
    <v-btn text to="/results">Results</v-btn>
    <v-btn text to="/reports">Reports</v-btn>
  </v-app-bar>
</template>

<script>
export default {
  name: "NavigationBar",
};
</script>
