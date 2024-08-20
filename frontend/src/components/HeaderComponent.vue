<template>
  <v-app-bar app color="primary" dark>
    <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
    <v-toolbar-title>Human-AI Benchmarking Suite</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn text to="/">Home</v-btn>
    <v-btn text to="/admin">Admin Panel</v-btn>
    <v-btn text to="/about">About</v-btn>
    <v-btn text to="/contact">Contact</v-btn>
  </v-app-bar>
</template>

<script>
export default {
  name: "HeaderComponent",
  data() {
    return {
      drawer: false,
    };
  },
};
</script>
