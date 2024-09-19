<template>
  <v-app-bar app color="primary" dark>
    <v-btn icon @click="$emit('toggleSidebar')">
      <v-icon>mdi-menu</v-icon>
    </v-btn>
    <v-toolbar-title>HAIC Evaluation Platform</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn icon @click="$emit('toggleTheme')">
      <v-icon>{{
        isDarkTheme ? "mdi-weather-sunny" : "mdi-weather-night"
      }}</v-icon>
    </v-btn>
  </v-app-bar>
</template>

<script>
export default {
  name: "HeaderComponent",
  props: {
    isDarkTheme: {
      type: Boolean,
      required: true,
    },
  },
};
</script>
