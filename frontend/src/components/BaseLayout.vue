<template>
  <v-app>
    <HeaderComponent @toggleSidebar="drawer = !drawer" />

    <v-navigation-drawer v-model="drawer" app temporary color="grey lighten-3">
      <AppSidebar />
    </v-navigation-drawer>

    <v-main>
      <v-container class="main-container">
        <slot></slot>
        <!-- This is where the content of each page will be injected -->
      </v-container>
    </v-main>

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
      drawer: false, // Default state of the sidebar is closed
    };
  },
};
</script>

<style scoped>
.main-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh; /* Ensure full page height */
  padding-top: 64px; /* Adjust according to your header height */
  padding-bottom: 64px; /* Adjust according to your footer height */
}
</style>
