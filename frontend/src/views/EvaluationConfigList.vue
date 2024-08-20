<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="12">
        <v-data-table :headers="headers" :items="configs" class="elevation-1">
          <template v-slot:top>
            <v-toolbar flat>
              <v-toolbar-title>Evaluation Configurations</v-toolbar-title>
              <v-divider class="mx-4" inset vertical></v-divider>
              <v-spacer></v-spacer>
              <v-btn color="primary" to="/configs/new">New Configuration</v-btn>
            </v-toolbar>
          </template>
          <template v-slot:item="{ item }">
            <v-btn icon @click="editConfig(item)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon @click="deleteConfig(item)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: "EvaluationConfigList",
  data() {
    return {
      headers: [
        { text: "Application Name", value: "application_name" },
        { text: "AI Model Name", value: "ai_model_name" },
        { text: "Description", value: "description" },
        { text: "Actions", value: "actions", sortable: false },
      ],
      configs: [], // This will be fetched from the API
    };
  },
  methods: {
    // editConfig(config) {
    //   // Navigate to edit page
    // },
    // deleteConfig(config) {
    //   // Call API to delete configuration
    // }
  },
};
</script>
