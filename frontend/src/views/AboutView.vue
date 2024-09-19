<template>
  <BaseLayout>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card class="mx-auto my-12" max-width="900" outlined>
            <v-card-title>
              <h2 class="text-h5 font-weight-bold">
                About Human-AI Benchmark Suite
              </h2>
            </v-card-title>
            <v-card-text>
              <p>
                The Human-AI Benchmark Suite is an application designed to
                evaluate Human-AI collaboration by logging interactions,
                configurations, and evaluations. This suite includes both a
                backend, built with FastAPI, and a frontend, built with Vue 3
                and Vuetify.
              </p>
              <v-divider class="my-4"></v-divider>
              <h3 class="text-h6 font-weight-bold">Purpose</h3>
              <p>
                The primary purpose of this application is to provide a
                comprehensive platform for assessing the performance and
                efficiency of AI models in various human-AI interaction
                scenarios. By capturing detailed logs and evaluation metrics,
                the suite helps researchers and developers understand how AI
                models perform in real-world applications.
              </p>
              <v-divider class="my-4"></v-divider>
              <h3 class="text-h6 font-weight-bold">Key Features</h3>
              <v-list dense>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-cog</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Evaluation Configuration:</strong> Create and
                      manage evaluation configurations with
                      ease.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-file-upload</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Log Ingestion:</strong> Upload and process log
                      files to generate evaluation results.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-chart-bar</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Dynamic Reporting:</strong> Generate detailed
                      reports and visualizations of evaluation
                      metrics.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-database</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Log Generation Tool:</strong> Create synthetic
                      log data tailored to specific application
                      types.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-api</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>API Endpoints:</strong> Access various endpoints
                      for managing configurations, logs, and
                      results.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              <v-divider class="my-4"></v-divider>
              <h3 class="text-h6 font-weight-bold">Technologies Used</h3>
              <v-list dense>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-server</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Backend:</strong> FastAPI, SQLAlchemy,
                      Alembic</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-web</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Frontend:</strong> Vue 3, Vuetify,
                      Chart.js</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-database</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Database:</strong> PostgreSQL</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-docker</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      ><strong>Containerization:</strong> Docker, Docker
                      Compose</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              <v-divider class="my-4"></v-divider>
              <h3 class="text-h6 font-weight-bold">Contributing</h3>
              <p>
                Contributions are welcome! Please follow these steps to
                contribute:
              </p>
              <v-list dense>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      >1. Fork the repository.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      >2. Create a feature branch (<code
                        >git checkout -b feature/your-feature</code
                      >).</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      >3. Commit your changes (<code
                        >git commit -am 'Add some feature'</code
                      >).</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      >4. Push to the branch (<code
                        >git push origin feature/your-feature</code
                      >).</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title
                      >5. Create a new Pull Request.</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              <v-btn color="primary" class="mt-4" @click="goToGitHub"
                >Contribute Now</v-btn
              >
              <v-divider class="my-4"></v-divider>
              <h3 class="text-h6 font-weight-bold">License</h3>
              <p>
                This project is licensed under the MIT License - see the LICENSE
                file for details.
              </p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";

export default {
  name: "AboutView",
  components: {
    BaseLayout,
  },
  methods: {
    goToGitHub() {
      window.open("https://github.com/gfragi/haic_benchmark_suite.git");
    },
  },
};
</script>

<style scoped>
.about {
  text-align: center;
  margin-top: 20px;
}
.v-list-item-title {
  font-size: 16px;
}
.v-list-item-icon {
  margin-right: 10px;
}
</style>
