<template>
  <BaseLayout>
    <v-container class="ml-auto">
      <!-- Logo and Slogan -->
      <v-img
        src="@/assets/humaine_logo_300x300.png"
        alt="HAIC Logo"
        contain
        max-width="140"
        class="mx-auto my-4"
      />
      <h1 class="text-center mb-2">Welcome to the HAIC Evaluation Platform</h1>
      <p class="text-center subtitle-1 mb-6">
        Benchmark, compare, and improve Human-AI Collaboration across multiple
        evaluation dimensions.
      </p>

      <!-- Guided Overview Section -->
      <v-sheet class="elevation-1 pa-6 mb-10" color="teal-lighten-3">
        <v-row align="center" justify="space-between">
          <v-col cols="12" md="8">
            <h2 class="text-h6 font-weight-bold mb-2">
              What you can do with this platform
            </h2>
            <ul class="pl-4">
              <li>
                🏁 Run HAIC evaluations using your logs and configuration setup
              </li>
              <li>🧠 Analyze usability and trust with survey-based scoring</li>
              <li>
                ⚖️ Evaluate fairness across demographic or task-based groups
              </li>
              <li>🧪 Simulate activity using synthetic log generation</li>
            </ul>
          </v-col>
          <v-col cols="12" md="4" class="text-md-right text-center">
            <v-btn
              large
              color="primary"
              class="elevation-6 px-8 py-2"
              @click="startConfigurationWizard"
            >
              <v-icon left class="mr-2">mdi-play-circle</v-icon>
              Start New Evaluation
            </v-btn>
          </v-col>
        </v-row>
      </v-sheet>

      <!-- Step 2: Analyze Results -->
      <v-subheader class="text-uppercase font-weight-bold mt-4 mb-2">
        Analyze Your Results
      </v-subheader>
      <v-row dense>
        <v-col cols="12" md="6">
          <v-card elevation="2" class="hover-card pa-2">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              <v-icon left class="mr-2">mdi-chart-bar</v-icon>
              Analyze User Perceptions (Survey Dashboard)
            </v-card-title>
            <v-card-text>
              View aggregated user feedback across pilots and app versions.
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/survey-dashboard">
                <v-icon left class="mr-2">mdi-chart-bar</v-icon>
                Go to Dashboard
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card elevation="2" class="hover-card pa-2">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              <v-icon left class="mr-2">mdi-scale-balance</v-icon>
              Assess AI Fairness
            </v-card-title>
            <v-card-text>
              Evaluate whether the system behaves equitably across groups.
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/fairness">
                <v-icon left class="mr-2">mdi-scale-balance</v-icon>
                Go to Fairness
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12">
          <v-card elevation="2" class="hover-card pa-2">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              <v-icon left class="mr-2">mdi-chart-areaspline</v-icon>
              Explore Evaluation Metrics
            </v-card-title>
            <v-card-text>
              Browse the definitions and goals of the metrics used in HAIC
              evaluations.
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/metrics">
                <v-icon left class="mr-2">mdi-chart-areaspline</v-icon>
                Go to Metrics
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <!-- Step 3: Manage or Simulate Data -->
      <v-sheet class="pa-6 mt-10" color="blue-grey-lighten-4">
        <v-subheader class="text-uppercase font-weight-bold mb-2">
          Manage or Simulate Evaluation Data
        </v-subheader>
        <v-row dense>
          <v-col cols="12" md="4">
            <v-card elevation="1" class="hover-card pa-2">
              <v-card-title class="text-subtitle-1 font-weight-bold">
                <v-icon left class="mr-2">mdi-cog</v-icon>
                Manage Configurations
              </v-card-title>
              <v-card-text>
                Adjust your evaluation setup or inspect saved configurations.
              </v-card-text>
              <v-card-actions>
                <v-btn color="primary" to="/configs">
                  <v-icon left class="mr-2">mdi-cog</v-icon>
                  Go to Configurations
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card elevation="1" class="hover-card pa-2">
              <v-card-title class="text-subtitle-1 font-weight-bold">
                <v-icon left class="mr-2">mdi-file-upload</v-icon>
                Manage Logs
              </v-card-title>
              <v-card-text>
                Upload or browse logs, results, and evaluation datasets.
              </v-card-text>
              <v-card-actions>
                <v-btn color="primary" to="/logs">
                  <v-icon left class="mr-2">mdi-file-upload</v-icon>
                  Go to Logs
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card elevation="1" class="hover-card pa-2">
              <v-card-title class="text-subtitle-1 font-weight-bold">
                <v-icon left class="mr-2">mdi-database-edit</v-icon>
                Simulate Logs
              </v-card-title>
              <v-card-text>
                Generate synthetic logs for experimentation using templates.
              </v-card-text>
              <v-card-actions>
                <v-btn color="primary" to="/log-generator">
                  <v-icon left class="mr-2">mdi-database-edit</v-icon>
                  Generate Logs
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-sheet>

      <!-- Footer Info -->
      <v-footer padless class="text-caption justify-center mt-8">
        <span>Version 1.2.0 • Backend: Online • © 2025 humAIne</span>
      </v-footer>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  name: "HomeView",
  components: {
    BaseLayout,
  },
  methods: {
    startConfigurationWizard() {
      this.$router.push("/configuration/new");
    },
  },
};
</script>

<style scoped>
.text-center {
  text-align: center;
}
.my-4 {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}
.mb-2 {
  margin-bottom: 0.75rem;
}
.mb-6 {
  margin-bottom: 2rem;
}
.mr-2 {
  margin-right: 0.5rem;
}
.hover-card {
  transition: transform 0.2s ease;
  min-height: 200px;
}
.hover-card:hover {
  transform: scale(1.03);
}
</style>
