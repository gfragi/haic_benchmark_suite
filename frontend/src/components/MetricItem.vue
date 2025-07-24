<template>
  <v-list-item class="metric-item">
    <div>
      <div class="metric-content">
        <v-btn
          icon
          x-small
          fab
          elevation="1"
          @click="dialog = true"
          class="pa-0 small-icon-button"
        >
          <v-icon class="small-icon">mdi-calculator</v-icon>
        </v-btn>
        <div class="metric-text">
          <v-list-item-title>{{ title }}</v-list-item-title>
          <v-list-item-subtitle>{{ description }}</v-list-item-subtitle>
        </div>
      </div>
    </div>

    <!-- Formula Dialog -->
    <v-dialog v-model="dialog" max-width="500">
      <v-card>
        <v-card-title class="headline">{{ title }} Formula</v-card-title>
        <v-card-text>
          <p>{{ formula }}</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-list-item>
</template>

<script>
export default {
  name: "MetricItem",
  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      required: true,
    },
    formula: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      dialog: false,
    };
  },
};
</script>

<style scoped>
.v-list-item-title {
  font-weight: bold;
}

.small-icon {
  font-size: 28px; /* Adjust the icon size to be smaller */
}

.metric-content {
  display: flex;
  align-items: center;
}

.small-icon-button {
  margin-right: 22px; /* Adjust space between icon and text */
}

.metric-text {
  display: flex;
  flex-direction: column;
}

.metric-item {
  margin-bottom: 18px; /* Adjust space between each list item */
  min-height: 36px; /* Adjust the minimum height of the list item */
}
</style>
