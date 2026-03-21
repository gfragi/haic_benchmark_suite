<template>
  <div class="empty-state text-center pa-12">
    <v-icon size="72" color="blue-grey-lighten-3" class="mb-5">
      {{ icon }}
    </v-icon>

    <h2 class="text-h5 font-weight-medium mb-3">{{ title }}</h2>

    <p
      class="text-body-1 text-medium-emphasis mb-2"
      style="max-width: 480px; margin-left: auto; margin-right: auto"
    >
      {{ message }}
    </p>

    <p class="text-caption text-medium-emphasis mb-6">
      {{ hint }}
    </p>

    <v-btn
      color="primary"
      size="large"
      rounded="lg"
      :to="actionTo || undefined"
      @click="!actionTo ? $emit('action') : undefined"
    >
      <v-icon start>{{ actionIcon }}</v-icon>
      {{ actionLabel }}
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "EmptyState",

  props: {
    icon: {
      type: String,
      default: "mdi-chart-timeline-variant-shimmer",
    },
    title: {
      type: String,
      default: "Nothing to show yet",
    },
    message: {
      type: String,
      default:
        "This platform benchmarks Human-AI Collaboration across domains like healthcare, energy, and smart cities — computing metrics like Trust, Cognitive Load, Adaptability, and more.",
    },
    hint: {
      type: String,
      default: "Create a configuration to get started.",
    },
    actionLabel: {
      type: String,
      default: "Create a Configuration",
    },
    actionTo: {
      type: [String, Object],
      default: "/configuration/new",
    },
    actionIcon: {
      type: String,
      default: "mdi-plus-circle-outline",
    },
  },

  emits: ["action"],
};
</script>

<style scoped>
.empty-state {
  min-height: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
