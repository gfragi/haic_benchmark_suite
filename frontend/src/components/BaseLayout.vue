<template>
  <v-app>
    <HeaderComponent @toggleSidebar="drawer = !drawer" />

    <!-- Include NavigationBar
    <NavigationBar /> -->

    <!-- Sidebar -->
    <v-navigation-drawer v-model="drawer" app temporary color="grey lighten-3">
      <AppSidebar />
    </v-navigation-drawer>

    <!-- Main Content Area -->
    <v-main>
      <v-container class="main-container">
        <slot></slot>
        <!-- This is where the content of each page will be injected -->
      </v-container>
    </v-main>

    <!-- Footer -->
    <FooterComponent />
  </v-app>
</template>

<script>
// import NavigationBar from "@/components/NavigationBar.vue";

import HeaderComponent from "@/components/HeaderComponent.vue";
import FooterComponent from "@/components/FooterComponent.vue";
import AppSidebar from "@/components/AppSidebar.vue";

export default {
  name: "BaseLayout",
  components: {
    HeaderComponent,
    FooterComponent,
    AppSidebar,
    // NavigationBar,
  },
  data() {
    return {
      drawer: false, // Default state of the sidebar is closed
    };
  },
};
</script>

<!-- <style scoped>
.main-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh; /* Ensure full page height */
  padding-top: 64px; /* Adjust according to your header height */
  padding-bottom: 64px; /* Adjust according to your footer height */
}
</style> -->
