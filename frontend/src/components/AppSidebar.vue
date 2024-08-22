<template>
  <v-navigation-drawer app>
    <v-list>
      <v-list-item-group>
        <v-list-item to="/">Home</v-list-item>
        <v-list-item to="/configs">Configurations</v-list-item>
        <v-list-item to="/logs">Log Ingestion</v-list-item>
        <v-list-item to="/results">Results</v-list-item>
        <v-list-item to="/reports">Reports</v-list-item>
        <v-list-item to="/about">About</v-list-item>
      </v-list-item-group>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
export default {
  name: "AppSidebar",
};
</script>
