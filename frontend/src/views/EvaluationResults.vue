<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="3">
        <Sidebar />
      </v-col>
      <v-col cols="12" md="9">
        <v-data-table :headers="headers" :items="results" class="elevation-1">
          <template v-slot:item="{ item }">
            <v-btn icon @click="viewResult(item)">
              <v-icon>mdi-eye</v-icon>
            </v-btn>
          </template>
        </v-data-table>
        <PlotlyChart :data="plotData" :layout="plotLayout" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Sidebar from "@/components/AppSidebar.vue";
import PlotlyChart from "@/components/PlotlyChart.vue";

export default {
  name: "EvaluationResults",
  components: { Sidebar, PlotlyChart },
  data() {
    return {
      headers: [
        { text: "Evaluation Date", value: "evaluation_date" },
        { text: "AI Model Name", value: "ai_model_name" },
        { text: "Metrics", value: "metrics" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      results: [], // This will be fetched from the API
      plotData: [], // Data for Plotly chart
      plotLayout: {}, // Layout for Plotly chart
    };
  },
  methods: {
    // viewResult(result) {
    //   // Navigate to detailed view or open a modal
    // }
  },
};
</script>
