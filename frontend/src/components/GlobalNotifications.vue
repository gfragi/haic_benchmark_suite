<template>
  <div class="global-notifications">
    <v-snackbar
      v-for="notification in notifications"
      :key="notification.id"
      v-model="notification.visible"
      :color="getNotificationColor(notification.type)"
      :timeout="notification.timeout || 5000"
      location="top"
      multi-line
    >
      <div class="d-flex align-center">
        <v-icon
          :color="getNotificationIconColor(notification.type)"
          class="mr-2"
        >
          {{ getNotificationIcon(notification.type) }}
        </v-icon>
        <div class="flex-grow-1">
          <div class="font-weight-medium">{{ notification.message }}</div>
          <div v-if="notification.details" class="text-caption mt-1 opacity-75">
            {{ notification.details }}
          </div>
        </div>
        <v-btn
          v-if="notification.showClose"
          icon
          variant="text"
          size="small"
          @click="dismissNotification(notification.id)"
        >
          <v-icon size="16">mdi-close</v-icon>
        </v-btn>
      </div>

      <template #actions>
        <v-btn
          v-if="notification.action"
          variant="text"
          size="small"
          @click="handleAction(notification.action)"
        >
          {{ notification.action.label }}
        </v-btn>
        <v-btn
          variant="text"
          size="small"
          @click="dismissNotification(notification.id)"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
/**
 * GlobalNotifications Component
 *
 * Displays global notifications from the Vuex UI store.
 * Supports different notification types with appropriate styling and actions.
 */
import { computed } from "vue";
import { useStore } from "vuex";

export default {
  name: "GlobalNotifications",

  setup() {
    const store = useStore();

    const notifications = computed(() => {
      return store.getters["ui/allNotifications"].map((notification) => ({
        ...notification,
        visible: true, // Control visibility for each notification
      }));
    });

    const getNotificationColor = (type) => {
      const colors = {
        success: "success",
        error: "error",
        warning: "warning",
        info: "info",
      };
      return colors[type] || "info";
    };

    const getNotificationIcon = (type) => {
      const icons = {
        success: "mdi-check-circle",
        error: "mdi-alert-circle",
        warning: "mdi-alert",
        info: "mdi-information",
      };
      return icons[type] || "mdi-information";
    };

    const getNotificationIconColor = (type) => {
      const colors = {
        success: "white",
        error: "white",
        warning: "white",
        info: "white",
      };
      return colors[type] || "white";
    };

    const dismissNotification = (id) => {
      store.dispatch("ui/removeNotification", id);
    };

    const handleAction = (action) => {
      if (action.handler) {
        action.handler();
      }
    };

    return {
      notifications,
      getNotificationColor,
      getNotificationIcon,
      getNotificationIconColor,
      dismissNotification,
      handleAction,
    };
  },
};
</script>

<style scoped>
.v-snackbar {
  margin-bottom: 8px;
}

.opacity-75 {
  opacity: 0.75;
}
</style>
