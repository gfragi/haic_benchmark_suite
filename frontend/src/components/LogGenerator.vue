<template>
  <BaseLayout>
    <v-container>
      <v-row>
        <v-col>
          <h2>Log Generation Tool</h2>
          <p class="subtitle-1">
            Generate adapter-ready synthetic logs (Core HAIC + outcome-friendly
            fields).
          </p>
        </v-col>
      </v-row>

      <v-form @submit.prevent="generateLogs">
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="form.app_type"
              :items="appTypes"
              item-title="title"
              item-value="value"
              label="Application Type"
              hint="Choose the domain to shape the decisions"
              persistent-hint
              required
            />
          </v-col>

          <v-col cols="12" md="4">
            <v-text-field
              v-model.number="form.count"
              type="number"
              min="1"
              label="Number of sessions"
              hint="How many session logs to generate"
              persistent-hint
              required
            />
          </v-col>

          <v-col cols="12" md="4">
            <v-text-field
              v-model="form.app_version"
              label="App Version"
              hint="Will also be used if your model version is tied to the app"
              persistent-hint
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.start_date"
              type="datetime-local"
              label="Start datetime (UTC)"
              hint="Window start (used to randomize session times)"
              persistent-hint
              required
            />
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.end_date"
              type="datetime-local"
              label="End datetime (UTC)"
              hint="Window end"
              persistent-hint
              required
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="form.ai_model_version_range"
              label="AI model version range"
              placeholder="1.0.0-2.0.0"
              hint="A.B.C-D.E.F — one version is sampled per session"
              persistent-hint
              required
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-text-field
              v-model.number="form.rt_max"
              type="number"
              step="0.1"
              min="0"
              label="rt_max (s)"
              hint="Upper bound for HCL normalization"
              persistent-hint
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-text-field
              v-model.number="form.baseline_s"
              type="number"
              step="0.1"
              min="0"
              label="baseline_s (s)"
              hint="Baseline task time for EL metric"
              persistent-hint
            />
          </v-col>
        </v-row>

        <v-row class="mt-2">
          <v-col>
            <v-btn color="primary" type="submit" :loading="loading">
              Generate Logs
            </v-btn>
            <v-btn
              class="ml-2"
              color="secondary"
              :disabled="!filePath"
              @click="downloadLogs"
            >
              Download Last File
            </v-btn>
          </v-col>
        </v-row>
      </v-form>

      <v-row v-if="logs && logs.length" class="mt-6">
        <v-col cols="12">
          <h3>Preview (first session):</h3>
          <pre class="pre">{{ pretty(logs[0]) }}</pre>
        </v-col>
      </v-row>

      <v-snackbar
        v-model="snackbar.show"
        :color="snackbar.color"
        top
        timeout="4000"
      >
        {{ snackbar.text }}
      </v-snackbar>
    </v-container>
  </BaseLayout>
</template>

<script>
import BaseLayout from "@/components/BaseLayout.vue";
import logGeneratorService from "@/services/logGeneratorService";

function toISOZ(dtLocal) {
  // dtLocal like "2025-09-12T10:00" (no TZ) -> "2025-09-12T10:00:00Z"
  if (!dtLocal) return "";
  const d = new Date(dtLocal);
  return new Date(
    Date.UTC(
      d.getFullYear(),
      d.getMonth(),
      d.getDate(),
      d.getHours(),
      d.getMinutes(),
      d.getSeconds() || 0
    )
  )
    .toISOString()
    .replace(".000Z", "Z");
}

export default {
  name: "LogGenerator",
  components: { BaseLayout },
  data() {
    const now = new Date();
    const earlier = new Date(now.getTime() - 24 * 3600 * 1000);
    const toLocalInput = (d) =>
      new Date(d.getTime() - d.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16);

    return {
      appTypes: [
        { title: "HMI / XR", value: "hmi_xr" },
        { title: "Radiology Assist", value: "radiologist" },
        { title: "Custom (generic)", value: "custom_app" },
      ],
      form: {
        app_type: "hmi_xr",
        count: 3,
        app_version: "1.0.0",
        start_date: toLocalInput(earlier),
        end_date: toLocalInput(now),
        ai_model_version_range: "1.0.0-2.0.0",
        rt_max: 5.0,
        baseline_s: 0.0,
      },
      logs: [],
      filePath: null,
      loading: false,
      snackbar: { show: false, color: "info", text: "" },
    };
  },
  methods: {
    pretty(obj) {
      try {
        return JSON.stringify(obj, null, 2);
      } catch {
        return String(obj);
      }
    },
    async generateLogs() {
      this.loading = true;
      this.filePath = null;
      try {
        // Build query params the backend expects
        const params = {
          app_type: this.form.app_type,
          count: this.form.count,
          start_date: toISOZ(this.form.start_date),
          end_date: toISOZ(this.form.end_date),
          ai_model_version_range: this.form.ai_model_version_range,
          rt_max: this.form.rt_max,
          baseline_s: this.form.baseline_s,
          app_version: this.form.app_version,
        };

        const { data } = await logGeneratorService.generateLogs(params);
        this.logs = data?.logs || [];
        this.filePath = data?.file_path || null;

        this.toast(
          `Generated ${data?.count ?? this.logs.length} session(s).`,
          "success"
        );
      } catch (err) {
        console.error("Error generating logs:", err);
        const msg =
          err?.response?.data || err?.message || "Failed to generate logs.";
        this.toast(
          typeof msg === "string" ? msg : "Failed to generate logs.",
          "error"
        );
      } finally {
        this.loading = false;
      }
    },
    async downloadLogs() {
      try {
        if (this.filePath) {
          await logGeneratorService.downloadLogs(this.filePath);
          return;
        }
        // Fallback: re-trigger generate and then download
        await this.generateLogs();
        if (this.filePath)
          await logGeneratorService.downloadLogs(this.filePath);
      } catch (err) {
        console.error("Download error:", err);
        this.toast("Could not download logs.", "error");
      }
    },
    toast(text, color = "info") {
      this.snackbar = { show: true, color, text };
    },
  },
};
</script>

<style scoped>
.subtitle-1 {
  margin-top: -5px;
  color: #757575;
}
.pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}
</style>
