<template>
  <BaseLayout>
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-2">Fairness Evaluation</h1>
          <p class="subtitle-1">
            Upload model predictions to evaluate fairness across selected
            sensitive features.
          </p>
        </v-col>
      </v-row>

      <!-- Upload JSONs -->
      <v-row>
        <v-col v-for="(file, index) in files" :key="index" cols="12" md="4">
          <v-file-input
            v-model="files[index]"
            :label="`Upload Model ${String.fromCharCode(65 + index)} JSON`"
            accept=".json"
            filled
            dense
            @change="onFileChange(files[index])"
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-btn
            color="primary"
            @click="addModelSlot"
            :disabled="files.length >= 3"
          >
            + Add Model
          </v-btn>
        </v-col>
      </v-row>

      <!-- Sensitive feature selection -->
      <v-row>
        <v-col cols="12" md="6">
          <v-select
            v-model="selectedFeature"
            :items="availableFeatures"
            label="Select Sensitive Feature"
            filled
            dense
            :disabled="!featuresLoaded"
          />
        </v-col>
        <v-col cols="12" md="6">
          <v-btn
            color="success"
            @click="submitEvaluation"
            :disabled="!selectedFeature || !files[0]"
          >
            Run Fairness Evaluation
          </v-btn>
        </v-col>
      </v-row>

      <!-- Results -->
      <v-row v-if="results">
        <v-col cols="12">
          <FairnessResults :results="results" />
        </v-col>
      </v-row>

      <v-snackbar v-model="snackbar" :color="snackbarColor">
        {{ snackbarText }}
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import FairnessResults from "@/components/FairnessResults.vue";
import fairnessService from "@/services/fairnessService";

export default {
  components: { BaseLayout, FairnessResults },
  data() {
    return {
      files: [null],
      selectedFeature: null,
      availableFeatures: [],
      featuresLoaded: false,
      results: null,
      snackbar: false,
      snackbarText: "",
      snackbarColor: "info",
    };
  },
  methods: {
    addModelSlot() {
      if (this.files.length < 3) {
        this.files.push(null);
      }
    },
    async submitEvaluation() {
      this.results = null;
      const promises = this.files
        .filter((f) => f)
        .map((file, idx) =>
          this.readFile(file).then((json) => {
            console.log(
              `Model ${String.fromCharCode(65 + idx)} payload:`,
              json
            );
            return json;
          })
        );

      try {
        const modelPayloads = await Promise.all(promises);

        const evaluations = await Promise.all(
          modelPayloads.map((payload) =>
            fairnessService.runFairnessEvaluation(this.selectedFeature, payload)
          )
        );

        this.results = evaluations.map((r, i) => ({
          model: `Model ${String.fromCharCode(65 + i)}`,
          ...r.data,
        }));
      } catch (error) {
        console.error("Fairness evaluation error:", error);
        this.showMessage(
          "Failed to evaluate fairness. Check your files and try again.",
          "error"
        );
        console.log("Selected feature:", this.selectedFeature);
      }
    },
    readFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const json = JSON.parse(e.target.result);
            resolve(json);
          } catch (err) {
            reject(err);
          }
        };
        reader.onerror = reject;
        reader.readAsText(file);
      });
    },
    onFileChange(file) {
      if (!file) return;
      this.readFile(file)
        .then((json) => {
          if (!this.featuresLoaded) {
            this.availableFeatures = Object.keys(json.sensitive_features || {});
            this.featuresLoaded = true;
          }
        })
        .catch(() => {
          this.showMessage("Invalid JSON file.", "error");
        });
    },
    showMessage(text, color = "info") {
      this.snackbarText = text;
      this.snackbarColor = color;
      this.snackbar = true;
    },
  },
};
</script>

<style scoped></style>
