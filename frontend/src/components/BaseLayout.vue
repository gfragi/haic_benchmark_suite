<template>
  <v-app>
    <!-- Header Component -->
    <HeaderComponent @toggleSidebar="drawer = !drawer" />

    <!-- Sidebar -->
    <v-navigation-drawer v-model="drawer" app color="primary" class="sidebar">
      <AppSidebar />
    </v-navigation-drawer>

    <!-- Main Content Area -->
    <v-main>
      <v-container
        fluid
        class="main-container"
        :class="{ 'drawer-open': drawer }"
      >
        <slot></slot>
        <!-- Content of each page will be injected here -->
      </v-container>
    </v-main>

    <!-- Footer -->
    <FooterComponent />
  </v-app>
</template>

<script>
import HeaderComponent from "@/components/HeaderComponent.vue";
import FooterComponent from "@/components/FooterComponent.vue";
import AppSidebar from "@/components/AppSidebar.vue";

export default {
  name: "BaseLayout",
  components: {
    HeaderComponent,
    FooterComponent,
    AppSidebar,
  },
  data() {
    return {
      drawer: true, // Default state of the sidebar is open
    };
  },
};
</script>

<style scoped>
.sidebar {
  width: 240px; /* Adjust the width as needed */
}

.main-container {
  min-height: 10vh;
  padding-top: 64px; /* Adjust according to your header height */
  padding-bottom: 64px; /* Adjust according to your footer height */
  padding-left: 0;
  padding-right: 0;
  margin-left: 80px; /* Adjust to match the sidebar width */
}
</style>
