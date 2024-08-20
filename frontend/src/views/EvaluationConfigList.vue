<template>
  <v-container>
    <v-data-table :headers="headers" :items="configs" class="elevation-1">
      <template v-slot:item="{ item }">
        <tr>
          <td>{{ item.application_name }}</td>
          <td>{{ item.ai_model_name }}</td>
          <td>{{ item.description }}</td>
          <td>{{ item.evaluation_date }}</td>
          <td>
            <v-btn icon @click="editConfig(item)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon @click="deleteConfig(item)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import evaluationConfigService from "@/services/evaluationConfigService";

export default {
  name: "EvaluationConfigList",
  data() {
    return {
      headers: [
        { text: "Application Name", value: "application_name" },
        { text: "AI Model Name", value: "ai_model_name" },
        { text: "Description", value: "description" },
        { text: "Evaluation Date", value: "evaluation_date" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      configs: [], // This will be fetched from the API
    };
  },
  methods: {
    fetchConfigs() {
      evaluationConfigService
        .getAllConfigs()
        .then((response) => {
          this.configs = response.data;
        })
        .catch((error) => {
          console.error("Error fetching configs:", error);
        });
    },
    editConfig(config) {
      this.$router.push(`/configs/${config.id}/edit`);
    },
    deleteConfig(config) {
      evaluationConfigService.deleteConfig(config.id).then(() => {
        this.fetchConfigs(); // Refresh the list after deletion
      });
    },
  },
  mounted() {
    this.fetchConfigs();
  },
};
</script>
