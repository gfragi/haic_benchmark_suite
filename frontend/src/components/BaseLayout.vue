<template>
  <v-app :theme="currentTheme">
    <!-- Global Notifications -->
    <GlobalNotifications />

    <!-- Header Component -->
    <HeaderComponent
      @toggleSidebar="toggleDrawer"
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
import { useStore } from "vuex";
import HeaderComponent from "@/components/HeaderComponent.vue";
import FooterComponent from "@/components/FooterComponent.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import GlobalNotifications from "@/components/GlobalNotifications.vue";

export default {
  name: "BaseLayout",
  components: {
    HeaderComponent,
    FooterComponent,
    AppSidebar,
    GlobalNotifications,
  },
  setup() {
    const store = useStore();

    // Use Vuex store for theme management
    const isDarkTheme = computed(() => store.getters['ui/isDarkTheme']);
    const currentTheme = computed(() => store.state.ui.theme);
    const drawer = computed(() => store.state.ui.drawer);

    const toggleTheme = () => {
      store.dispatch('ui/toggleTheme');
    };

    const toggleDrawer = () => {
      store.dispatch('ui/toggleDrawer');
    };

    // Initialize theme on component mount
    onMounted(() => {
      store.dispatch('ui/initializeTheme');
    });

    return {
      drawer,
      isDarkTheme,
      currentTheme,
      toggleTheme,
      toggleDrawer,
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
