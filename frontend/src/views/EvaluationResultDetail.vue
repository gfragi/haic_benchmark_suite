<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col>
          <h2>Evaluation Result Details</h2>
          <v-card class="mb-4">
            <v-card-title
              >Result for Configuration
              {{ result.configuration_id }}</v-card-title
            >
            <v-card-text>
              <v-list dense>
                <v-list-item v-for="(value, key) in result" :key="key">
                  <v-list-item-content>
                    <v-list-item-title>{{ key }}</v-list-item-title>
                    <v-list-item-subtitle>{{ value }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import evaluationService from "@/services/resultService";

export default {
  components: {
    BaseLayout,
  },
  data() {
    return {
      result: {},
    };
  },
  mounted() {
    this.fetchResultDetail();
  },
  methods: {
    fetchResultDetail() {
      const resultId = this.$route.params.resultId;
      evaluationService
        .getEvaluationResultDetail(resultId)
        .then((response) => {
          this.result = response.data;
        })
        .catch((error) => {
          console.error("Error fetching evaluation result detail:", error);
        });
    },
  },
};
</script>

<style scoped>
.v-card-title {
  background-color: #f5f5f5;
}
.v-list-item-title {
  font-weight: bold;
}
</style>
