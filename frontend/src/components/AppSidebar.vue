<template>
  <v-list dense>
    <v-divider></v-divider>

    <router-link
      v-for="item in items"
      :key="item.title"
      :to="item.route"
      class="v-list-item"
    >
      <v-list-item>
        <v-list-item-icon>
          <v-icon>{{ item.icon }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </router-link>
  </v-list>
</template>

<script>
export default {
  name: "AppSidebar",
  data() {
    return {
      items: [
        { title: "Home", icon: "mdi-home", route: "/" },
        { title: "Configurations", icon: "mdi-cog", route: "/configs" },
        { title: "Log Management", icon: "mdi-file-import", route: "/logs" },
        {
          title: "Explore Metrics",
          icon: "mdi-chart-areaspline",
          route: "/metrics",
        },
        {
          title: "Log Generation",
          icon: "mdi-database-edit",
          route: "/log-generator",
        },
        { title: "About", icon: "mdi-information", route: "/about" },
      ],
    };
  },
};
</script>

<style scoped>
.v-list-item {
  color: rgb(234, 236, 239);
  text-decoration: none;
}
</style>
