<template>
  <BaseLayout>
    <v-container>
      <!-- Header and Instructions -->
      <v-alert type="info" class="mb-4" dense>
        This dashboard displays average SUS and Ethics scores. You can compare
        different app versions within a pilot, or switch to pilot-level
        comparison.
      </v-alert>

      <!-- Comparison Mode Toggle -->
      <v-radio-group v-model="comparisonMode" row class="mb-4">
        <v-radio label="Compare App Versions (per Pilot)" value="versions" />
        <v-radio label="Compare Pilots (overall)" value="pilots" />
      </v-radio-group>

      <!-- Chart Type Switch -->
      <v-switch
        v-model="isLineChart"
        :label="`Chart type: ${isLineChart ? 'line' : 'bar'}`"
        class="mb-4"
      />

      <!-- Pilot Filter (only for version comparison) -->
      <SurveyFilter
        v-if="comparisonMode === 'versions'"
        @update:pilotTag="loadData"
      />

      <!-- Loading Indicator -->
      <div v-if="loading" class="text-center my-8">
        <v-progress-circular indeterminate color="primary" size="40" />
      </div>

      <!-- Chart Title and Count -->
      <div v-if="!loading" class="text-center my-4">
        <h3 class="text-h6">{{ chartTitle }}</h3>
        <p class="text-caption">Total surveys: {{ totalSurveys }}</p>
      </div>

      <!-- Chart -->
      <SurveyChart
        v-if="Object.keys(aggregatedData).length"
        :data="sortedAggregatedData"
        :type="chartType"
      />

      <!-- No Data Message -->
      <div v-else-if="!loading" class="text-center my-8">
        <p>No data available.</p>
      </div>

      <!-- Export Button -->
      <v-btn class="mt-4" @click="exportData" color="primary">Export CSV</v-btn>

      <!-- Navigate to Compare Page -->
      <v-btn
        variant="text"
        :to="{ name: 'SurveyCompare', query: { pilot: selectedPilotTag } }"
      >
        <v-icon start>mdi-compare</v-icon> Compare Versions
      </v-btn>
      <!-- Public Survey Link Button -->
      <v-btn
        variant="text"
        :disabled="comparisonMode !== 'versions' || !selectedPilotTag"
        @click="openShare"
      >
        <v-icon start>mdi-link-variant</v-icon> Collect Responses
      </v-btn>

      <v-dialog v-model="shareOpen" max-width="640">
        <v-card>
          <v-card-title>Public Survey Link</v-card-title>
          <v-card-text>
            <div class="mb-2">
              Share this link with pilot users to answer directly:
            </div>
            <v-text-field
              :model-value="surveyHref"
              readonly
              prepend-inner-icon="mdi-link-variant"
              append-inner-icon="mdi-content-copy"
              @click:append-inner="copy(surveyHref)"
            />
            <div
              class="my-4"
              style="display: flex; gap: 16px; align-items: center"
            >
              <v-img
                :src="qrDataUrl"
                width="140"
                height="140"
                alt="Survey QR"
                class="rounded"
              />
              <div class="text-body-2">
                Scan to open the survey on mobile.
                <div class="mt-2">
                  <v-btn size="small" variant="outlined" @click="downloadQR">
                    <v-icon start>mdi-download</v-icon> Download QR
                  </v-btn>
                </div>
              </div>
            </div>
            <v-alert type="info" variant="tonal">
              You can also append <code>&app_version=...</code> and
              <code>&ai_model_version=...</code> to prefill metadata.
            </v-alert>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn variant="flat" color="primary" @click="copy(publicLink)"
              >Copy</v-btn
            >
            <v-btn variant="text" @click="shareOpen = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Evaluation Questions -->
      <v-expansion-panels class="mt-6">
        <v-expansion-panel>
          <v-expansion-panel-title>SUS Questions</v-expansion-panel-title>
          <v-expansion-panel-text>
            <ol>
              <li>I think I would like to use this system frequently.</li>
              <li>I found the system unnecessarily complex.</li>
              <li>I thought the system was easy to use.</li>
              <li>
                I think I would need the support of a technical person to use
                this system.
              </li>
              <li>
                I found the various functions in this system were well
                integrated.
              </li>
              <li>
                I thought there was too much inconsistency in this system.
              </li>
              <li>
                I would imagine most people would learn to use this system
                quickly.
              </li>
              <li>I found the system very difficult to use.</li>
              <li>I felt very confident using the system.</li>
              <li>
                I needed to learn many things before I could get going with this
                system.
              </li>
            </ol>
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel>
          <v-expansion-panel-title>Ethics Questions</v-expansion-panel-title>
          <v-expansion-panel-text>
            <ol>
              <li>
                Fairness: The system handles different tasks or users without
                bias.
              </li>
              <li>
                Transparency: I understand how the system/AI arrives at its
                decisions.
              </li>
              <li>
                Privacy: I feel confident that personal data is protected.
              </li>
              <li>
                Accountability: It is clear who or what is responsible for
                errors.
              </li>
              <li>
                Trust: Overall, I trust the system to operate ethically and in
                my best interest.
              </li>
            </ol>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-container>
  </BaseLayout>
</template>

<script setup>
import BaseLayout from "@/components/BaseLayout.vue";
import SurveyFilter from "@/components/SurveyFilter.vue";
import SurveyChart from "@/components/SurveyChart.vue";
import { fetchSurveyAggregates } from "@/services/survey";
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";
import debounce from "lodash.debounce";
import semver from "semver";
import QRCode from "qrcode";

const comparisonMode = ref("versions");
const aggregatedData = ref({});
const loading = ref(false);
const isLineChart = ref(false);
const chartType = computed(() => (isLineChart.value ? "line" : "bar"));
const shareOpen = ref(false);
const qrDataUrl = ref("");
const selectedAppVersion = ref("");
const selectedModelVersion = ref("");
const selectedPilotTag = ref("");
const router = useRouter();

const surveyHref = computed(() => {
  const { href } = router.resolve({
    name: "PublicSurvey",
    query: {
      pilot_tag: selectedPilotTag.value || undefined,
      app_version: selectedAppVersion.value || undefined,
      ai_model_version: selectedModelVersion.value || undefined,
    },
  }).href;
  // return `${window.location.origin}${href}`;
  const hash = new URLSearchParams({
    pilot_tag: selectedPilotTag.value || "",
    app_version: selectedAppVersion.value || "",
    ai_model_version: selectedModelVersion.value || "",
  }).toString();

  return `${window.location.origin}${href}#${hash}`;
});

const totalSurveys = computed(() =>
  Object.values(aggregatedData.value).reduce(
    (acc, val) => acc + (val.count || 0),
    0
  )
);

const chartTitle = computed(() => {
  if (comparisonMode.value === "versions") {
    return `Avg SUS & Ethics per App Version for "${
      selectedPilotTag.value || "..."
    }"`;
  } else {
    return "Avg SUS & Ethics per Pilot";
  }
});

const sortedAggregatedData = computed(() => {
  const entries = Object.entries(aggregatedData.value);
  if (comparisonMode.value === "versions") {
    return Object.fromEntries(
      entries.sort(([a], [b]) => {
        if (semver.valid(a) && semver.valid(b)) {
          return semver.compare(a, b);
        }
        return a.localeCompare(b); // fallback
      })
    );
  }
  return aggregatedData.value;
});

const loadData = debounce(async (pilotTag = null) => {
  loading.value = true;
  try {
    selectedPilotTag.value = pilotTag;
    const raw = await fetchSurveyAggregates(
      comparisonMode.value === "versions" ? pilotTag : null
    );
    aggregatedData.value = raw;
  } catch (error) {
    console.error("Failed to load data:", error);
    aggregatedData.value = {};
  } finally {
    loading.value = false;
  }
}, 300);

// Initial load: default is all pilots
loadData();

function exportData() {
  const csv = Object.entries(aggregatedData.value)
    .map(
      ([key, vals]) =>
        `${key},${vals.avg_sus.toFixed(2)},${vals.avg_ethics.toFixed(2)},${
          vals.count
        }`
    )
    .join("\n");

  const header =
    comparisonMode.value === "versions"
      ? "App Version,Avg SUS,Avg Ethics,Count\n"
      : "Pilot,Avg SUS,Avg Ethics,Count\n";

  const blob = new Blob([header + csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "survey_aggregates.csv";
  link.click();
}

function slug(s) {
  return String(s || "")
    .trim()
    .replace(/\s+/g, "-") // spaces -> dashes
    .replace(/[^\w-]/g, ""); // strip odd chars
}

const publicLink = computed(() => {
  const pilot = slug(selectedPilotTag.value);
  const base = pilot
    ? `${window.location.origin}/survey/:pilot_tag?${encodeURIComponent(pilot)}`
    : `${window.location.origin}/survey`;
  const params = new URLSearchParams();
  if (selectedAppVersion.value)
    params.set("app_version", selectedAppVersion.value);
  if (selectedModelVersion.value)
    params.set("model_version", selectedModelVersion.value);
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
});

watch(surveyHref, async (url) => {
  try {
    qrDataUrl.value = await QRCode.toDataURL(url, { margin: 1, scale: 5 });
  } catch (e) {
    console.error("QR gen error:", e);
  }
});

function openShare() {
  shareOpen.value = true;
  // ensure QR exists if dialog opened before computed ran
  QRCode.toDataURL(surveyHref.value, { margin: 1, scale: 5 })
    .then((d) => {
      qrDataUrl.value = d;
    })
    .catch((e) => console.error("QR gen error:", e));
}

function downloadQR() {
  const a = document.createElement("a");
  a.href = qrDataUrl.value;
  a.download = `survey_link_${selectedPilotTag.value || "pilot"}.png`;
  a.click();
}

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    console.error("Clipboard copy failed:", err); // handle or report
  }
}
</script>
