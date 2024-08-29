<template>
  <BaseLayout>
    <v-container>
      <v-card class="mx-auto my-5" max-width="900">
        <v-card-title class="text-h5">
          Human-AI Collaboration Metrics
        </v-card-title>
        <v-card-text>
          <v-expansion-panels multiple>
            <!-- Performance Metrics -->
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-chart-line</v-icon>
                Performance Metrics
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list dense>
                  <MetricItem
                    title="Prediction Accuracy"
                    description="Measures how accurately the AI predicts outcomes based on true positives and true negatives."
                    formula="Accuracy = (True Positives + True Negatives) / Total Predictions"
                  />
                  <MetricItem
                    title="Precision"
                    description="Indicates the proportion of true positive predictions out of all positive predictions made by the AI."
                    formula="Precision = True Positives / (True Positives + False Positives)"
                  />
                  <MetricItem
                    title="Recall"
                    description="Reflects the proportion of true positives identified out of all actual positives."
                    formula="Recall = True Positives / (True Positives + False Negatives)"
                  />
                  <MetricItem
                    title="Overall System Accuracy"
                    description="Percentage of correct outcomes produced by the system."
                    formula="Overall System Accuracy = (Number of Correct Outcomes / Total Number of Outcomes) * 100"
                  />
                  <MetricItem
                    title="Model Improvement Rate"
                    description="The rate at which the AI model improves its performance over a given time period."
                    formula="Model Improvement Rate = (Performance at Time T - Performance at Time T-1) / Time Interval"
                  />
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>

            <!-- Efficiency Metrics -->
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-timer-sand</v-icon>
                Efficiency Metrics
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list dense>
                  <MetricItem
                    title="Response Time"
                    description="Average time taken by the AI to respond to queries."
                    formula="Response Time = Total Response Time / Number of Queries"
                  />
                  <MetricItem
                    title="Teaching Efficiency"
                    description="Efficiency of performance improvement relative to the time spent teaching the AI."
                    formula="Teaching Efficiency = Performance Improvement / Time Spent"
                  />
                  <MetricItem
                    title="Query Efficiency"
                    description="Number of queries needed to reach a target accuracy."
                    formula="Query Efficiency = Total Queries / Queries to Reach Target Accuracy"
                  />
                  <MetricItem
                    title="Resource Utilization"
                    description="The percentage of resources used by the AI relative to the total available resources."
                    formula="Resource Utilization = (Resources Used / Total Resources Available) * 100"
                  />
                  <MetricItem
                    title="Task Completion Time"
                    description="Time saved by using AI compared to completing the task without AI."
                    formula="Task Completion Time = Time Without AI - Time With AI"
                  />
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>

            <!-- Adaptability and Learning Metrics -->
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-lightbulb-on-outline</v-icon>
                Adaptability and Learning Metrics
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list dense>
                  <MetricItem
                    title="Feedback Impact"
                    description="Improvement in AI performance after receiving human feedback."
                    formula="Feedback Impact = Performance Post-Feedback - Performance Pre-Feedback"
                  />
                  <MetricItem
                    title="Adaptability Score"
                    description="AI's ability to adapt and improve after receiving feedback or adjustments."
                    formula="Adaptability Score = Performance Post-Adaptation - Performance Pre-Adaptation"
                  />
                  <MetricItem
                    title="Impact of Corrections"
                    description="Improvement in system performance following human corrections."
                    formula="Impact of Corrections = Performance Post-Correction - Performance Pre-Correction"
                  />
                  <MetricItem
                    title="Learning Efficiency"
                    description="The efficiency of human learning when assisted by AI."
                    formula="Learning Efficiency = Learning Gains / Time Spent Learning"
                  />
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>

            <!-- Collaboration and Interaction Metrics -->
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-account-group</v-icon>
                Collaboration and Interaction Metrics
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list dense>
                  <MetricItem
                    title="Human-AI Agreement Rate"
                    description="The rate of agreement between human decisions and AI suggestions."
                    formula="Human-AI Agreement Rate = Agreements / Total Decisions"
                  />
                  <MetricItem
                    title="AI Assistance Rate"
                    description="The frequency with which AI assists in human decisions."
                    formula="AI Assistance Rate = Assisted Decisions / Total Decisions"
                  />
                  <MetricItem
                    title="Decision Effectiveness"
                    description="The effectiveness of decisions made with AI support, measured as a percentage of successful decisions."
                    formula="Decision Effectiveness = (Successful Decisions / Total Decisions) * 100"
                  />
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>

            <!-- Trust and Safety Metrics -->
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-shield-check-outline</v-icon>
                Trust and Safety Metrics
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list dense>
                  <MetricItem
                    title="Confidence"
                    description="Percentage of high-confidence correct predictions made by the AI."
                    formula="Confidence = (Correct High Confidence Predictions / Total High Confidence Predictions) * 100"
                  />
                  <MetricItem
                    title="Trust Score"
                    description="Level of trust users place in the AI system, measured as a percentage."
                    formula="Trust Score = (Total Trust Ratings / Total Trust Scale) * 100"
                  />
                  <MetricItem
                    title="Safety Incidents"
                    description="The number of safety-related incidents reported during AI operation."
                    formula="Safety Incidents = Sum of Safety Incidents"
                  />
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>

            <!-- Robustness and Generalization Metrics -->
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-shield-alert-outline</v-icon>
                Robustness and Generalization Metrics
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-list dense>
                  <MetricItem
                    title="Adversarial Robustness"
                    description="AI performance in adversarial conditions compared to normal conditions."
                    formula="Adversarial Robustness = Performance Adversarial / Performance Normal"
                  />
                  <MetricItem
                    title="Domain Generalization"
                    description="The AI's ability to generalize its performance across different domains relative to a baseline."
                    formula="Domain Generalization = Performance Across Domains / Baseline Performance"
                  />
                </v-list>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
      </v-card>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import MetricItem from "@/components/MetricItem.vue"; // Create this as a separate file

export default {
  name: "MetricsPage",
  components: {
    BaseLayout,
    MetricItem,
  },
};
</script>

<style scoped>
.v-list-item-title {
  font-weight: bold;
}
</style>
