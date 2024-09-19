<template>
  <v-app :theme="currentTheme">
    <!-- Header Component -->
    <HeaderComponent
      @toggleSidebar="drawer = !drawer"
      @toggleTheme="toggleTheme"
      :isDarkTheme="isDarkTheme"
    />

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
import { ref, computed, onMounted } from "vue";
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
  setup() {
    const isDarkTheme = ref(false);

    const currentTheme = computed(() => (isDarkTheme.value ? "dark" : "light"));

    const toggleTheme = () => {
      isDarkTheme.value = !isDarkTheme.value;
      localStorage.setItem("isDarkTheme", isDarkTheme.value);
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("isDarkTheme");
      if (savedTheme !== null) {
        isDarkTheme.value = savedTheme === "true";
      }
    });

    return {
      drawer: ref(true),
      isDarkTheme,
      currentTheme,
      toggleTheme,
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
  padding-left: 0px;
  padding-right: 180px;
  margin-left: 80px; /* Adjust to match the sidebar width */
}
</style>
